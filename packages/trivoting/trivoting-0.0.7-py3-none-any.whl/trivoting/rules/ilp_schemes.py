"""Generic schemes to compute outcomes of rules via integer linear programs."""

from __future__ import annotations

import abc
from enum import Enum

from pulp import (
    LpProblem,
    LpMaximize,
    LpAffineExpression,
    LpVariable,
    LpBinary,
    lpSum,
    HiGHS,
    PULP_CBC_CMD,
    LpStatusOptimal,
    value,
)

from trivoting.election import AbstractTrichotomousProfile, Selection
from trivoting.fractions import Numeric


class ILPNotOptimalError(ValueError):
    """Exception raised when the outcome of the ILP solver is not proven to be an optimal solution."""

    pass


class ILPSolver(Enum):
    """Enumerates the different solvers available."""

    HIGHS = "HIGHS"
    """HiGHS: open-source software to solve linear programming"""

    CBC = "CBC"
    """Cbc (Coin-or branch and cut) is an open-source mixed integer linear programming solver"""


class ILPBuilder(abc.ABC):
    """
    Abstract class used to define ILP programs that are then passed to the
    :py:func:`~trivoting.rules.ilp_schemes.ilp_optimiser_rule` function for the actual solving.

    Parameters
    ----------
    profile : AbstractTrichotomousProfile
        The trichotomous profile.
    max_size_selection : int
        Maximum number of alternatives to select.
    initial_selection : Selection, optional
        An initial selection that fixes some alternatives as selected or rejected.
        If `implicit_reject` is True, no alternatives are fixed to be rejected.
    max_seconds : int, optional
        Maximum number of seconds to run the ILP solver for.
        Defaults to 600 seconds (10 minutes).
    verbose : bool, optional
        If True the output of the ILP solver is not silenced.
        Defaults to False.
    solver_name : ILPSolver
        Name of the ILP solver to use.

    Attributes
    ----------
    model_name : str
        Name of the model, used when writing the LP files.
    profile : AbstractTrichotomousProfile
        The trichotomous profile.
    max_size_selection : int
        Maximum number of alternatives to select.
    initial_selection : Selection, optional
        An initial selection that fixes some alternatives as selected or rejected.
        If `implicit_reject` is True, no alternatives are fixed to be rejected.
    model : LpProblem
        The actual PuLP model.
    vars: dict[str, dict]
        The variables used in the ILP model, mapping type of variable to dictionary containing LpVariable.
    """

    model_name = "NoName"

    def __init__(
        self,
        profile: AbstractTrichotomousProfile,
        max_size_selection: int,
        initial_selection: Selection = None,
        max_seconds: int = 600,
        verbose: bool = False,
        solver_name: ILPSolver = None,
    ) -> None:

        self.profile = profile
        self.max_size_selection = max_size_selection
        self.initial_selection = initial_selection
        if solver_name is None:
            solver_name = ILPSolver.HIGHS
        if solver_name == ILPSolver.HIGHS:
            self.solver = HiGHS(msg=verbose, timeLimit=max_seconds)
        elif solver_name == ILPSolver.CBC:
            self.solver = PULP_CBC_CMD(msg=verbose, timeLimit=max_seconds)
        else:
            raise ValueError(f"Unsupported solver name {solver_name}.")

        self.model = LpProblem(self.model_name, sense=LpMaximize)
        self.vars = dict()

    def init_selection_vars(self):
        """Initialises the selections variables. Other function assumes that self.vars["selection"] exists and
        correspond to the variables indicating whether an alternative is selected or not.
        """
        self.vars["selection"] = {
            alt: LpVariable(f"y_{alt.name}", cat=LpBinary)
            for alt in self.profile.alternatives
        }

    def init_vars(self) -> None:
        """Initialises the variables. This function is meant to be overridden. The super() needs to be called to
        ensure the initialisation of all the variables that are shared by all ILP models.
        """
        self.init_selection_vars()

    def constrain_initial_selection(self):
        """Adds the constraints related to the initial selection to the model."""
        if self.initial_selection is not None:
            for alt in self.initial_selection.selected:
                self.model += self.vars["selection"][alt] == 1
            if not self.initial_selection.implicit_reject:
                for alt in self.initial_selection.rejected:
                    self.model += self.vars["selection"][alt] == 0

    def constrain_max_size_selection(self):
        """Adds the constraint related to the maximum size of the selections."""
        self.model += lpSum(self.vars["selection"].values()) <= self.max_size_selection

    def apply_constraints(self):
        """Applies the different constraints to the model."""
        self.constrain_initial_selection()
        self.constrain_max_size_selection()

    @abc.abstractmethod
    def objective(self) -> LpAffineExpression:
        """Returns the objective function of the ILP."""

    def set_objective(self):
        """Sets the objective function to the model itself."""
        self.model += self.objective()

    def solve(self) -> int:
        """
        Optimises the model and return the optimisation status.

        Returns
        -------
        int
            The optimisation status of the solver.
        """
        return self.model.solve(self.solver)

    def force_objective_value(self, v: Numeric):
        """
        Adds a constraint to the model to force the objective to have a specific value.

        Parameters
        ----------
        v : Numeric
            The value of the objective.
        """
        self.model += self.objective() == v

    def ban_selection(self, selection: Selection) -> None:
        """
        Adds the constraints to ban a given selection.

        Parameters
        ----------
        selection : Selection
            The selection to ban.
        """
        # See http://yetanothermathprogrammingconsultant.blogspot.com/2011/10/integer-cuts.html
        self.model += (
            lpSum((1 - self.vars["selection"][a]) for a in selection.selected)
            + lpSum(v for a, v in self.vars["selection"].items() if a not in selection)
        ) >= 1

        self.model += (
            lpSum(self.vars["selection"][a] for a in selection.selected)
            - lpSum(v for a, v in self.vars["selection"].items() if a not in selection)
        ) <= len(selection) - 1


def ilp_optimiser_rule(
    ilp_builder: ILPBuilder,
    resoluteness: bool = True,
) -> Selection | list[Selection]:
    """Rule that optimises an ILP and returns the corresponding selection(s). Returns the first optimal solution found
    if :code:`resoluteness = True` and, all the optimal solutions otherwise."""

    if (
        ilp_builder.initial_selection
        and len(ilp_builder.initial_selection) >= ilp_builder.max_size_selection
    ):
        return (
            ilp_builder.initial_selection
            if resoluteness
            else [ilp_builder.initial_selection]
        )

    ilp_builder.init_vars()
    ilp_builder.apply_constraints()
    ilp_builder.set_objective()

    status = ilp_builder.solve()

    all_selections = []

    if status == LpStatusOptimal:
        selection = Selection(implicit_reject=True)
        for alt, v in ilp_builder.vars["selection"].items():
            if value(v) >= 0.9:
                selection.add_selected(alt)
        all_selections.append(selection)
    else:
        raise ILPNotOptimalError(
            f"Solver did not find an optimal solution, status is {status}."
        )

    if resoluteness:
        return all_selections[0]

    # If irresolute, we solve again, banning the previous selections
    ilp_builder.force_objective_value(value(ilp_builder.model.objective))
    previous_selection = selection
    while True:
        ilp_builder.ban_selection(previous_selection)

        status = ilp_builder.solve()

        if status != LpStatusOptimal:
            break

        previous_selection = Selection(
            [
                a
                for a, v in ilp_builder.vars["selection"].items()
                if value(v) is not None and value(v) >= 0.9
            ],
            implicit_reject=True,
        )
        if previous_selection not in all_selections:
            all_selections.append(previous_selection)

    return all_selections

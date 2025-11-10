"""The max net support rule returns selections maximising the total net support of the voters. The net support of a
voter for a given selection is defined as the number of approved and selected alternatives minus the number of
disapproved but selected ones."""

from __future__ import annotations

from pulp import lpSum, LpVariable, LpInteger, LpAffineExpression

from trivoting.election import AbstractTrichotomousProfile, Selection
from trivoting.rules.ilp_schemes import (
    ILPBuilder,
    ilp_optimiser_rule,
    ILPNotOptimalError,
)


class MaxNetSupportILPBuilder(ILPBuilder):
    """Builder class for the ILP corresponding to the max net support rule. Used in the function
    :py:func:`~trivoting.rules.max_net_support.max_net_support_ilp`."""

    model_name = "MaxNetSupport"

    def init_vars(self) -> None:
        super(MaxNetSupportILPBuilder, self).init_vars()

        self.vars["sat_var"] = dict()

        for i, ballot in enumerate(self.profile):
            sat_var = LpVariable(
                f"sat_{i}",
                lowBound=-self.max_size_selection,
                upBound=self.max_size_selection,
                cat=LpInteger,
            )
            self.model += sat_var == lpSum(
                self.vars["selection"][alt] for alt in ballot.approved
            ) - lpSum(self.vars["selection"][alt] for alt in ballot.disapproved)
            self.vars["sat_var"][i] = sat_var

    def objective(self) -> LpAffineExpression:
        return lpSum(
            self.vars["sat_var"][i] * self.profile.multiplicity(b)
            for i, b in enumerate(self.profile)
        )


def max_net_support_ilp(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    initial_selection: Selection = None,
    resoluteness: bool = True,
    max_seconds: int = 600,
    verbose: bool = False,
) -> Selection | list[Selection]:
    """
    Compute the selections maximising the total net support of the voters via an ILP solver.

    Used mostly for debugging purposes, the function :py:func:`~trivoting.rules.max_net_support.max_net_support` being
    much more efficient.

    Parameters
    ----------
    profile : AbstractTrichotomousProfile
        The trichotomous profile.
    max_size_selection : int
        Maximum number of alternatives to select.
    initial_selection : Selection, optional
        An initial selection that fixes some alternatives as selected or rejected.
        If `implicit_reject` is True, no alternatives are fixed to be rejected.
    resoluteness : bool, optional
        If True, returns a single selection (resolute).
        If False, returns all tied optimal selections (irresolute).
        Defaults to True.
    max_seconds : int, optional
        Maximum number of seconds to run the ILP solver for.
        Defaults to 600 seconds (10 minutes).
    verbose : bool, optional
        If True the output of the ILP solver is not silenced.
        Defaults to False.

    Returns
    -------
    Selection | list[Selection]
        The selection if resolute (:code:`resoluteness == True`), or a list of selections
        if irresolute (:code:`resoluteness == False`).
    """
    ilp_builder = MaxNetSupportILPBuilder(
        profile,
        max_size_selection,
        initial_selection,
        max_seconds=max_seconds,
        verbose=verbose,
    )
    try:
        return ilp_optimiser_rule(ilp_builder, resoluteness=resoluteness)
    except ILPNotOptimalError as e:
        raise RuntimeError("Max Net Support ILP did not converge.") from e


def max_net_support(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    initial_selection: Selection = None,
    resoluteness: bool = True,
) -> Selection | list[Selection]:
    """
    Compute the selections maximising the total net support of the voters by sequentially selecting up to
    `max_size_selection` alternatives with positive highest net support.

    The net support of an alternative is the number of voters approving of it minus the number of voters disapproving
    of it.

    Parameters
    ----------
    profile : AbstractTrichotomousProfile
        The trichotomous profile.
    max_size_selection : int
        Maximum number of alternatives to select.
    initial_selection : Selection, optional
        An initial selection that fixes some alternatives as selected or rejected.
        If `implicit_reject` is True, no alternatives are fixed to be rejected.
    resoluteness : bool, optional
        If True, returns a single selection (resolute).
        If False, returns all tied optimal selections (irresolute).
        Defaults to True.
    Returns
    -------
    Selection | list[Selection]
        The selection if resolute (:code:`resoluteness == True`), or a list of selections
        if irresolute (:code:`resoluteness == False`).
    """
    if not resoluteness:
        raise NotImplementedError(
            "Max Net Support does not yet support resoluteness=False."
        )
    alt_scores = profile.support_dict()
    if initial_selection is None:
        selection = Selection(implicit_reject=True)
    else:
        selection = initial_selection
    for alt, score in sorted(alt_scores.items(), key=lambda x: x[1], reverse=True):
        if len(selection) >= max_size_selection:
            break
        if score > 0:
            selection.add_selected(alt)
    return selection

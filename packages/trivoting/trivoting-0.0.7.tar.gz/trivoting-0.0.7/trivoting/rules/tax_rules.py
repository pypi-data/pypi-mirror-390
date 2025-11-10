"""
Tax rules are rules that transform the trichotomous profile into a participatory budgeting (PB) instance and then use
PB rules to compute selections for the trichotomous profile.
"""

from __future__ import annotations

import abc
from collections.abc import Callable

import pabutools.election as pb_election
import pabutools.rules as pb_rules

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_profile import AbstractTrichotomousProfile
from trivoting.fractions import frac, Numeric
from trivoting.election.selection import Selection
from trivoting.tiebreaking import TieBreakingRule, lexico_tie_breaking
from trivoting.utils import generate_subsets


class TaxFunction(abc.ABC):
    """
    Abstract class representing tax functions. A tax function associates a tax (i.e., the cost of a project on the PB side)
    to alternatives.
    """

    def __init__(self, profile: AbstractTrichotomousProfile, max_size_selection: int):
        self.profile = profile
        self.max_size_selection = max_size_selection
        self.preprocessed_data = dict()
        self.preprocess()

    def preprocess(self) -> None:
        """Preprocessing of the profile used to save up time on expensive computations that would be otherwise repeated."""
        pass

    @abc.abstractmethod
    def tax_alternative(self, alternative: Alternative) -> Numeric | None:
        """
        Returns the tax corresponding to the alternative. If `None` is returned, no project corresponding to the
        alternative is added to the PB instance.
        """


class TaxKraiczy2025(TaxFunction):
    """
    Tax function proposed in ``Proportionality in Thumbs Up and Down Voting`` (Kraiczy, Papasotiropoulos, Pierczyński
    and Skowron, 2025). The cost of a project is equal to its approval score divided by its support (approval minus disapproval score).
    If the support is negative, then the project is skipped.
    """

    def preprocess(self) -> None:
        app_scores, disapp_scores = self.profile.approval_disapproval_score_dict()
        self.preprocessed_data = {
            "app_scores": app_scores,
            "disapp_scores": disapp_scores,
        }

    def tax_alternative(self, alternative: Alternative) -> Numeric | None:
        app_score = self.preprocessed_data["app_scores"][alternative]
        disapp_score = self.preprocessed_data["disapp_scores"][alternative]
        support = app_score - disapp_score
        if support > 0:
            return frac(app_score, support)
        return None


class DisapprovalLinearTax(TaxFunction):
    """
    Disapproval linear tax function for which the cost of a project is equal to its disapproval multiplied by a fixed
    factor.
    """

    def __init__(
        self,
        profile: AbstractTrichotomousProfile,
        max_size_selection: int,
        weight=None,
        class_method_call=False,
    ):
        if not class_method_call:
            raise RuntimeError(
                "To create a disapproval linear tax, use the initialize() class method instead of using the class itself."
            )
        TaxFunction.__init__(self, profile, max_size_selection)
        self.weight = weight

    @classmethod
    def initialize(
        cls, weight: Numeric
    ) -> Callable[AbstractTrichotomousProfile, int, DisapprovalLinearTax]:
        def constructor(
            profile: AbstractTrichotomousProfile, max_size_selection: int
        ) -> DisapprovalLinearTax:
            return cls(
                profile, max_size_selection, weight=weight, class_method_call=True
            )

        return constructor

    def preprocess(self) -> None:
        self.preprocessed_data["disapp_scores"] = self.profile.disapproval_score_dict()

    def tax_alternative(self, alternative: Alternative) -> Numeric | None:
        return 1 + self.weight * self.preprocessed_data["disapp_scores"][alternative]


def tax_pb_instance(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    initial_selection: Selection | None = None,
    tax_function: type[TaxFunction] = None,
) -> tuple[
    pb_election.Instance,
    pb_election.ApprovalMultiProfile,
    dict[pb_election.Project, Alternative],
]:
    """
    Construct a Participatory Budgeting (PB) instance and PB profile from a trichotomous profile.

    This function translates the trichotomous voting profile into a PB instance,
    setting project costs inversely proportional to net support.

    Parameters
    ----------
    profile : AbstractTrichotomousProfile
        The trichotomous profile.
    max_size_selection : int
        The budget limit or maximum number of alternatives to be selected.
    initial_selection : Selection or None, optional
        An initial selection fixing some alternatives as selected or rejected.
    tax_function: type[TaxFunction], optional
        A tax function defined as a subclass of the :py:class:`TaxFunction` class. Defaults to
        :py:class:`TaxKraiczy2025`.

    Returns
    -------
    pb_election.Instance
        The generated PB instance containing projects.
    pb_election.ApprovalMultiProfile
        The PB profile created from approval ballots derived from the trichotomous profile.
    dict
        A mapping from PB projects back to the original alternatives.
    """

    if initial_selection is None:
        initial_selection = Selection()
    if tax_function is None:
        tax_function = TaxKraiczy2025

    tax_function = tax_function(profile, max_size_selection)
    alt_to_project = dict()
    project_to_alt = dict()
    running_alternatives = set()
    pb_instance = pb_election.Instance(
        budget_limit=max_size_selection - len(initial_selection)
    )
    for alt in profile.alternatives:
        if alt not in initial_selection:
            cost = tax_function.tax_alternative(alt)
            if cost is not None:
                project = pb_election.Project(
                    alt.name, cost=tax_function.tax_alternative(alt)
                )
                pb_instance.add(project)
                running_alternatives.add(alt)
                alt_to_project[alt] = project
                project_to_alt[project] = alt
    pb_profile = pb_election.ApprovalMultiProfile(instance=pb_instance)
    for ballot in profile:
        pb_profile.append(
            pb_election.FrozenApprovalBallot(
                alt_to_project[alt]
                for alt in ballot.approved
                if alt in running_alternatives
            )
        )
    return pb_instance, pb_profile, project_to_alt


def tax_pb_rule_scheme(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    pb_rule: Callable,
    tax_function: type[TaxFunction],
    initial_selection: Selection | None = None,
    tie_breaking: TieBreakingRule | None = None,
    resoluteness: bool = True,
    pb_rule_kwargs: dict = None,
) -> Selection | list[Selection]:
    """
    Apply a participatory budgeting rule to a trichotomous profile by translating it into a suitable PB instance with
    opposition tax.

    This function converts the given profile into a PB instance and profile,
    applies the specified PB rule using pabutools, and converts the results back.

    The taxed PB rule scheme has been defined in Section 4.2 of
    ``Proportionality in Thumbs Up and Down Voting`` (Kraiczy, Papasotiropoulos, Pierczyński and Skowron, 2025).

    In case there are alternatives whose corresponding projects have cost 0, it can happen that too many projects are
    selected on the PB side. In this case, the tie breaking function is used to select the right number of alternatives.

    Parameters
    ----------
    profile : AbstractTrichotomousProfile
        The trichotomous profile.
    max_size_selection : int
        The maximum number of alternatives allowed in the selection.
    pb_rule : callable
        The participatory budgeting rule function to apply.
    tax_function: type[TaxFunction]
        A tax function defined as a subclass of the :py:class:`TaxFunction` class.
    initial_selection : Selection or None, optional
        An initial selection fixing some alternatives as selected or rejected.
    tie_breaking : TieBreakingRule or None, optional
        Tie-breaking rule used for resolving ties.
        Defaults to lexicographic tie-breaking if None.
    resoluteness : bool, optional
        Whether to return a single resolute selection (True) or all tied selections (False).
        Defaults to True.
    pb_rule_kwargs : dict, optional
        Additional keyword arguments passed to the PB rule.

    Returns
    -------
    Selection or list of Selection
        The resulting selection(s) after applying the PB rule.
    """
    if pb_rule_kwargs is None:
        pb_rule_kwargs = dict()
    if tie_breaking is None:
        tie_breaking = lexico_tie_breaking

    if initial_selection is None:
        initial_selection = Selection(implicit_reject=True)
    remaining_max_size = max_size_selection - len(initial_selection)

    if profile.num_ballots() == 0:
        return initial_selection if resoluteness else [initial_selection]

    pb_instance, pb_profile, project_to_alt = tax_pb_instance(
        profile, max_size_selection, initial_selection, tax_function=tax_function
    )

    budget_allocation = pb_rule(
        pb_instance, pb_profile, resoluteness=resoluteness, **pb_rule_kwargs
    )

    if resoluteness:
        selected_alts = [project_to_alt[p] for p in budget_allocation]
        # We need to deal with the case when too many projects are selected on the PB side.
        if len(budget_allocation) > remaining_max_size:
            initial_selection.extend_selected(
                tie_breaking.order(profile, selected_alts)[:remaining_max_size]
            )
        else:
            initial_selection.extend_selected(selected_alts)
        if not initial_selection.implicit_reject:
            initial_selection.extend_rejected(
                project_to_alt[p] for p in pb_instance if p not in budget_allocation
            )
        return initial_selection
    else:
        all_selections = []
        for alloc in budget_allocation:
            selected_alts = [project_to_alt[p] for p in alloc]
            # We need to deal with the case when too many projects are selected on the PB side.
            if len(alloc) > remaining_max_size:
                subselections = generate_subsets(
                    selected_alts,
                    min_size=remaining_max_size,
                    max_size=remaining_max_size,
                )
            else:
                subselections = [selected_alts]
            for subselection in subselections:
                selection = initial_selection.copy()
                selection.extend_selected(subselection)
                if not selection.implicit_reject:
                    selection.extend_rejected(
                        project_to_alt[p] for p in pb_instance if p not in alloc
                    )
                all_selections.append(selection)
        return all_selections


def tax_method_of_equal_shares(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    tax_function: type[TaxFunction] = None,
    initial_selection: Selection | None = None,
    tie_breaking: TieBreakingRule | None = None,
    resoluteness: bool = True,
) -> Selection | list[Selection]:
    """
    Apply the Tax method of equal shares to a trichotomous profile.

    This method uses participatory budgeting rules to compute proportional selections
    with the method of equal shares adapted for approval-disapproval profiles.

    Parameters
    ----------
    profile : AbstractTrichotomousProfile
        The input profile.
    max_size_selection : int
        The maximum number of alternatives to select.
    tax_function: type[TaxFunction], optional
        A tax function defined as a subclass of the :py:class:`TaxFunction` class. Defaults to
        :py:class:`TaxKraiczy2025`.
    initial_selection : Selection or None, optional
        Initial fixed selection state.
    tie_breaking : TieBreakingRule or None, optional
        Tie-breaking rule. Defaults to lexicographic.
    resoluteness : bool, optional
        Whether to return a single or multiple tied selections.

    Returns
    -------
    Selection | list[Selection]
        The selection if resolute (:code:`resoluteness == True`), or a list of selections
        if irresolute (:code:`resoluteness == False`).
    """
    return tax_pb_rule_scheme(
        profile,
        max_size_selection,
        pb_rules.method_of_equal_shares,
        tax_function=tax_function,
        initial_selection=initial_selection,
        tie_breaking=tie_breaking,
        resoluteness=resoluteness,
        pb_rule_kwargs={"sat_class": pb_election.Cardinality_Sat},
    )


def tax_sequential_phragmen(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    tax_function: type[TaxFunction] = None,
    initial_selection: Selection | None = None,
    tie_breaking: TieBreakingRule | None = None,
    resoluteness: bool = True,
) -> Selection | list[Selection]:
    """
    Apply Tax sequential Phragmén method on a trichotomous profile.

    This rule transforms the profile into a participatory budgeting instance
    and applies sequential Phragmén via pabutools.

    Parameters
    ----------
    profile : AbstractTrichotomousProfile
        The input voting profile.
    max_size_selection : int
        The maximum size of the selection.
    tax_function: type[TaxFunction], optional
        A tax function defined as a subclass of the :py:class:`TaxFunction` class. Defaults to
        :py:class:`TaxKraiczy2025`.
    initial_selection : Selection or None, optional
        Initial fixed selections.
    tie_breaking : TieBreakingRule or None, optional
        Tie-breaking rule, defaulting to lexicographic.
    resoluteness : bool, optional
        Whether to return one selection or all tied selections.

    Returns
    -------
    Selection | list[Selection]
        The selection if resolute (:code:`resoluteness == True`), or a list of selections
        if irresolute (:code:`resoluteness == False`).
    """

    return tax_pb_rule_scheme(
        profile,
        max_size_selection,
        pb_rules.sequential_phragmen,
        tax_function=tax_function,
        initial_selection=initial_selection,
        tie_breaking=tie_breaking,
        resoluteness=resoluteness,
        pb_rule_kwargs={
            "global_max_load": (
                frac(max_size_selection, profile.num_ballots())
                if profile.num_ballots()
                else None
            )
        },
    )

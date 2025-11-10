"""
A Thiele rule returns selections that maximises a score defined as a function of (1) the number of approved and selected
alternatives, (2) the number of disapproved and selected alternatives, (3) the number of approved and rejected
alternatives, and (4) the number of disapproved and rejected alternatives.
"""

from __future__ import annotations

import abc
from abc import abstractmethod
from collections.abc import Iterable
from copy import deepcopy

from trivoting.election import AbstractTrichotomousProfile, Alternative

from pulp import (
    LpBinary,
    LpVariable,
    lpSum,
    LpAffineExpression,
    LpInteger,
)

from trivoting.election.selection import Selection
from trivoting.fractions import Numeric
from trivoting.rules.ilp_schemes import ILPBuilder, ilp_optimiser_rule
from trivoting.tiebreaking import TieBreakingRule, lexico_tie_breaking
from trivoting.utils import harmonic_sum, classproperty


class ThieleScore(abc.ABC):
    """Class used to define score function for Thiele methods. Defines the elements that are needed for both the ILP
    solver approach and the sequential approach."""

    def __init__(self, max_size_selection: int):
        self.max_size_selection = max_size_selection

    @abstractmethod
    def score_function(
        self,
        num_app_sel: int = 0,
        num_disapp_sel: int = 0,
        num_app_rej: int = 0,
        num_disapp_rej: int = 0,
    ):
        """
        Actual scoring function. Can only depend on:
            - the number of approved and selected alternatives;
            - the number of disapproved and selected alternatives;
            - the number of approved and rejected alternatives; and on
            - the number of disapproved and rejected alternatives.

        Parameters
        ----------
            num_app_sel: int, optional
                The number of approved and selected alternatives
            num_disapp_sel: int, optional
                The number of disapproved and selected alternatives
            num_app_rej: int, optional
                The number of approved and rejected alternatives
            num_disapp_rej: int, optional
                The number of disapproved and rejected alternatives
        """

    def score_selection(
        self,
        profile: AbstractTrichotomousProfile,
        selection: Selection,
        extra_accept: Iterable[Alternative] = None,
        extra_reject: Iterable[Alternative] = None,
    ) -> Numeric:
        """
        Returns the total score of a selection for a given profile according to the scoring function.

        Use the `extra_accept` and `extra_reject` parameters to extend the selection without having to copy it.

        Parameters
        ----------
            profile : AbstractTrichotomousProfile
                The profile.
            selection : Selection
                The selection.
            extra_accept : Iterable[Alternative], optional
                Additional alternative to consider as being part of the selection. Defaults to the empty list.
            extra_reject : Iterable[Alternative], optional
                Additional alternative to consider as being rejected in the selection. Defaults to the empty list.

        Returns
        -------

        """
        if extra_reject is None:
            extra_reject = []
        if extra_accept is None:
            extra_accept = []
        score = 0
        for ballot in profile:
            num_app_sel = 0
            num_app_rej = 0
            num_disapp_sel = 0
            num_disapp_rej = 0
            for a in ballot.approved:
                if (
                    selection.is_selected(a) and a not in extra_reject
                ) or a in extra_accept:
                    num_app_sel += 1
                elif (
                    selection.is_rejected(a) and a not in extra_accept
                ) or a in extra_reject:
                    num_app_rej += 1
            for a in ballot.disapproved:
                if (
                    selection.is_rejected(a) and a not in extra_accept
                ) or a in extra_reject:
                    num_disapp_rej += 1
                elif (
                    selection.is_selected(a) and a not in extra_reject
                ) or a in extra_accept:
                    num_disapp_sel += 1
            ballot_score = self.score_function(
                num_app_sel, num_disapp_sel, num_app_rej, num_disapp_rej
            )
            score += ballot_score * profile.multiplicity(ballot)
        return score

    class _ThieleILPBuilder(abc.ABC):
        pass

    @classproperty
    def ilp_builder(cls) -> type[ILPBuilder]:
        """
        Return the ILPBuilder class used for the ILP optimising version of the Thiele rule.
        """
        builder_cls = getattr(cls, "_ILPBuilder", None)
        if builder_cls is None or builder_cls is ThieleScore._ThieleILPBuilder:
            raise NotImplementedError(
                f"{cls.__name__} must define its own inner class _ILPBuilder to be used with and ILP solver."
            )
        return builder_cls


class PAVScoreKraiczy2025(ThieleScore):
    """
    PAV scoring function as defined in Section 3.3 of
    ``Proportionality in Thumbs Up and Down Voting`` (Kraiczy, Papasotiropoulos, Pierczyński and Skowron, 2025).
    The objective is to maximise the PAV score where both approved and selected, and disapproved and not selected
    alternatives contribute positively.
    """

    def score_function(
        self, num_app_sel=0, num_disapp_sel=0, num_app_rej=0, num_disapp_rej=0
    ):
        return harmonic_sum(num_app_sel + num_disapp_rej)

    class _ILPBuilder(ILPBuilder):

        def init_vars(self) -> None:
            super().init_vars()
            self.vars["sat_vars"] = dict()
            for i, ballot in enumerate(self.profile):
                sat_vars = dict()
                for k in range(1, len(self.profile.alternatives) + 1):
                    sat_vars[k] = LpVariable(f"s_{i}_{k}", cat=LpBinary)
                self.vars["sat_vars"][i] = sat_vars

            # Constraint them to ensure proper counting
            for i, ballot in enumerate(self.profile):
                self.model += lpSum(self.vars["sat_vars"][i].values()) == lpSum(
                    self.vars["selection"][alt] for alt in ballot.approved
                ) + lpSum(1 - self.vars["selection"][alt] for alt in ballot.disapproved)

        def objective(self) -> LpAffineExpression:
            return lpSum(
                lpSum(v / k for k, v in self.vars["sat_vars"][i].items())
                * self.profile.multiplicity(b)
                for i, b in enumerate(self.profile)
            )


class PAVScoreTalmonPaige2021(ThieleScore):
    """
    PAV scoring function as defined in Section 4.2 of
    ``Proportionality in Committee Selection with Negative Feelings`` (Talmon and Page, 2021).
    The objective is to maximise the difference between (1) the PAV score in which approved and selected alternatives
    are taken into account, and (2) the PAV score in which disapproved but selected alternatives are taken into account.
    """

    def score_function(
        self, num_app_sel=0, num_disapp_sel=0, num_app_rej=0, num_disapp_rej=0
    ):
        return harmonic_sum(num_app_sel) - harmonic_sum(num_disapp_sel)

    class _ILPBuilder(ILPBuilder):
        def init_vars(self) -> None:
            super().init_vars()
            self.vars["app_sat_vars"] = {}
            self.vars["disapp_dissat_vars"] = {}

            for i, ballot in enumerate(self.profile):
                app_vars = {
                    k: LpVariable(f"as_{i}_{k}", cat=LpBinary)
                    for k in range(1, len(self.profile.alternatives) + 1)
                }
                disapp_vars = {
                    k: LpVariable(f"dd_{i}_{k}", cat=LpBinary)
                    for k in range(1, len(self.profile.alternatives) + 1)
                }
                self.vars["app_sat_vars"][i] = app_vars
                self.vars["disapp_dissat_vars"][i] = disapp_vars

                # Constraints
                self.model += lpSum(app_vars.values()) == lpSum(
                    self.vars["selection"][alt] for alt in ballot.approved
                )
                self.model += lpSum(disapp_vars.values()) == lpSum(
                    self.vars["selection"][alt] for alt in ballot.disapproved
                )

        def objective(self) -> LpAffineExpression:
            app_term = lpSum(
                lpSum(v / k for k, v in self.vars["app_sat_vars"][i].items())
                * self.profile.multiplicity(ballot)
                for i, ballot in enumerate(self.profile)
            )
            disapp_term = lpSum(
                lpSum(v / k for k, v in self.vars["disapp_dissat_vars"][i].items())
                * self.profile.multiplicity(ballot)
                for i, ballot in enumerate(self.profile)
            )
            return app_term - disapp_term


class PAVScoreHervouin2025(ThieleScore):
    """
    PAV scoring function as defined by Matthieu Hervouin in his PhD Thesis.
    The objective is to maximise the sum of (1) the PAV score in which approved and selected alternatives
    are taken into account, and (2) the PAV score over the maximum size of the selection minus the number of
    disapproved but selected alternatives.
    """

    def score_function(
        self, num_app_sel=0, num_disapp_sel=0, num_app_rej=0, num_disapp_rej=0
    ):
        return harmonic_sum(num_app_sel) + harmonic_sum(
            self.max_size_selection - num_disapp_sel
        )

    class _ILPBuilder(ILPBuilder):
        def init_vars(self) -> None:
            super().init_vars()
            self.vars["app_sat_vars"] = {}
            self.vars["disapp_dissat_vars"] = {}

            for i, ballot in enumerate(self.profile):
                app_vars = {
                    k: LpVariable(f"as_{i}_{k}", cat=LpBinary)
                    for k in range(1, len(self.profile.alternatives) + 1)
                }
                disapp_vars = {
                    k: LpVariable(f"dd_{i}_{k}", cat=LpBinary)
                    for k in range(1, len(self.profile.alternatives) + 1)
                }
                self.vars["app_sat_vars"][i] = app_vars
                self.vars["disapp_dissat_vars"][i] = disapp_vars

                # Constraints
                self.model += lpSum(app_vars.values()) == lpSum(
                    self.vars["selection"][alt] for alt in ballot.approved
                )
                self.model += lpSum(
                    disapp_vars.values()
                ) == self.max_size_selection - lpSum(
                    self.vars["selection"][alt] for alt in ballot.disapproved
                )

        def objective(self) -> LpAffineExpression:
            app_term = lpSum(
                lpSum(v / k for k, v in self.vars["app_sat_vars"][i].items())
                * self.profile.multiplicity(ballot)
                for i, ballot in enumerate(self.profile)
            )
            disapp_term = lpSum(
                lpSum(v / k for k, v in self.vars["disapp_dissat_vars"][i].items())
                * self.profile.multiplicity(ballot)
                for i, ballot in enumerate(self.profile)
            )
            return app_term + disapp_term


class ApprovalThieleScore(ThieleScore):
    """Thiele scoring function in which the score of a selection is equal to its approval score: the sum over all
    ballots of the number of approved and selected alternatives."""

    def score_function(
        self, num_app_sel=0, num_disapp_sel=0, num_app_rej=0, num_disapp_rej=0
    ):
        return num_app_sel

    class _ILPBuilder(ILPBuilder):
        def init_vars(self) -> None:
            super().init_vars()
            self.vars["sat_vars"] = {}

            for i, ballot in enumerate(self.profile):
                sat_vars = {
                    k: LpVariable(f"s_{i}_{k}", lowBound=-1, upBound=1, cat=LpInteger)
                    for k in range(1, len(self.profile.alternatives) + 1)
                }
                self.vars["sat_vars"][i] = sat_vars

                # Constraints
                self.model += lpSum(sat_vars.values()) == (
                    lpSum(self.vars["selection"][alt] for alt in ballot.approved)
                )

        def objective(self) -> LpAffineExpression:
            return lpSum(
                lpSum(v for v in self.vars["sat_vars"][i].values())
                * self.profile.multiplicity(ballot)
                for i, ballot in enumerate(self.profile)
            )


class NetSupportThieleScore(ThieleScore):
    """Thiele scoring function in which the score of a selection is equal to its net support: the sum over all
    ballots of the number of approved and selected alternatives minus the number of disapproved but selected ones.
    """

    def score_function(
        self, num_app_sel=0, num_disapp_sel=0, num_app_rej=0, num_disapp_rej=0
    ):
        return num_app_sel - num_disapp_sel

    class _ILPBuilder(ILPBuilder):
        def init_vars(self) -> None:
            super().init_vars()
            self.vars["sat_vars"] = {}

            for i, ballot in enumerate(self.profile):
                sat_vars = {
                    k: LpVariable(f"s_{i}_{k}", lowBound=-1, upBound=1, cat=LpInteger)
                    for k in range(1, len(self.profile.alternatives) + 1)
                }
                self.vars["sat_vars"][i] = sat_vars

                # Constraints
                self.model += lpSum(sat_vars.values()) == (
                    lpSum(self.vars["selection"][alt] for alt in ballot.approved)
                    - lpSum(self.vars["selection"][alt] for alt in ballot.disapproved)
                )

        def objective(self) -> LpAffineExpression:
            return lpSum(
                lpSum(v for v in self.vars["sat_vars"][i].values())
                * self.profile.multiplicity(ballot)
                for i, ballot in enumerate(self.profile)
            )


def thiele_method(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    thiele_score_class: type[ThieleScore],
    initial_selection: Selection | None = None,
    resoluteness: bool = True,
    verbose: bool = False,
    max_seconds: int = 600,
) -> Selection | list[Selection]:
    """
    Compute the selections of a Thiele rule described described via a :py:class:`~trivoting.rules.thiele.ThieleScore`
    class. The selections are computed by solving integer linear programs (ILP).

    Parameters
    ----------
    profile : AbstractTrichotomousProfile
        The trichotomous profile.
    max_size_selection : int
        Maximum number of alternatives to select.
    thiele_score_class : type[ThieleScore]
        The Thiele score class used to define the Thiele rule.
    initial_selection : Selection, optional
        An initial partial selection fixing some alternatives as selected or rejected.
        If `implicit_reject` is True in the initial selection, no alternatives are fixed to be rejected.
        Defaults to None.
    resoluteness : bool, optional
        If True, returns a single optimal selection (resolute).
        If False, returns all tied optimal selections (irresolute).
        Defaults to True.
    verbose : bool, optional
        If True, enables ILP solver output.
        Defaults to False.
    max_seconds : int, optional
        Time limit in seconds for the ILP solver.
        Defaults to 600.

    Returns
    -------
    Selection | list[Selection]
        The selection if resolute (:code:`resoluteness == True`), or a list of selections
        if irresolute (:code:`resoluteness == False`).
    """

    ilp_builder = thiele_score_class.ilp_builder(
        profile,
        max_size_selection,
        initial_selection,
        max_seconds=max_seconds,
        verbose=verbose,
    )
    return ilp_optimiser_rule(ilp_builder, resoluteness=resoluteness)


def sequential_thiele(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    thiele_score_class: type[ThieleScore],
    initial_selection: Selection | None = None,
    tie_breaking: TieBreakingRule | None = None,
    resoluteness: bool = True,
) -> Selection | list[Selection]:
    """
    Compute the selections of a sequential Thiele rule described via a :py:class:`~trivoting.rules.thiele.ThieleScore`
    class.

    The alternatives are selected sequentially one after the other, each time selecting the alternative that would
    lead to the best improve in score. Alternatives from the current selection that have a negative marginal contribution
    to the score are removed.

    Parameters
    ----------
    profile : AbstractTrichotomousProfile
        The trichotomous profile.
    max_size_selection : int
        Maximum number of alternatives to select.
    thiele_score_class : type[ThieleScore]
        The Thiele score class used to define the Thiele rule.
    initial_selection : Selection, optional
        An initial selection that fixes some alternatives as selected or rejected.
        If `implicit_reject` is True, no alternatives are fixed to be rejected.
    tie_breaking : TieBreakingRule, optional
        Tie-breaking rule used when multiple alternatives tie.
        Defaults to lexicographic tie-breaking.
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

    def _select_next_alternative(
        alternatives: set[Alternative], selection: Selection, skip_remove_phase=False
    ):
        something_changed = False
        branched = False

        # Remove alternatives that have negative marginal contributions
        if not skip_remove_phase:
            min_marginal_contribution = None
            argmin_marginal_contribution = None
            for alternative in selection.selected:
                marginal_contribution = thiele_score.score_selection(
                    profile, selection
                ) - thiele_score.score_selection(
                    profile, selection, extra_reject=[alternative]
                )
                if (
                    min_marginal_contribution is None
                    or marginal_contribution < min_marginal_contribution
                ):
                    min_marginal_contribution = marginal_contribution
                    argmin_marginal_contribution = [alternative]
                elif min_marginal_contribution == marginal_contribution:
                    argmin_marginal_contribution.append(alternative)
            if min_marginal_contribution is not None and min_marginal_contribution < 0:
                tied_alternatives = tie_breaking.order(
                    profile, argmin_marginal_contribution
                )
                # print(f"Removing one of {tied_alternatives} ({min_marginal_contribution})")
                if resoluteness:
                    alt_to_remove = tied_alternatives[0]
                    selection.remove_selected(alt_to_remove)
                    alternatives.add(alt_to_remove)
                    something_changed = True
                else:
                    for alt_to_remove in tied_alternatives:
                        new_selection = deepcopy(selection)
                        new_selection.remove_selected(alt_to_remove)
                        new_alternatives = deepcopy(alternatives)
                        new_alternatives.add(alt_to_remove)
                        _select_next_alternative(
                            new_alternatives, new_selection, skip_remove_phase=True
                        )
                        branched = True
        else:
            something_changed = True

        # Add alternative with maximum marginal contribution
        if len(selection) < max_size_selection:
            max_marginal_contribution = None
            argmax_marginal_contribution = None
            for alternative in alternatives:
                marginal_contribution = thiele_score.score_selection(
                    profile, selection, extra_accept=[alternative]
                ) - thiele_score.score_selection(profile, selection)
                # print(alternative, thiele_score.score_selection(profile, selection, extra_accept=[alternative]), thiele_score.score_selection(profile, selection))
                if (
                    max_marginal_contribution is None
                    or marginal_contribution > max_marginal_contribution
                ):
                    max_marginal_contribution = marginal_contribution
                    argmax_marginal_contribution = [alternative]
                elif max_marginal_contribution == marginal_contribution:
                    argmax_marginal_contribution.append(alternative)
            if max_marginal_contribution is not None and max_marginal_contribution > 0:
                tied_alternatives = tie_breaking.order(
                    profile, argmax_marginal_contribution
                )
                # print(f"Adding one of {tied_alternatives} ({max_marginal_contribution})")
                if resoluteness:
                    alt_to_add = tied_alternatives[0]
                    selection.add_selected(alt_to_add)
                    alternatives.remove(alt_to_add)
                    something_changed = True
                else:
                    for alt_to_add in tied_alternatives:
                        new_selection = deepcopy(selection)
                        new_selection.add_selected(alt_to_add)
                        new_alternatives = deepcopy(alternatives)
                        new_alternatives.remove(alt_to_add)
                        _select_next_alternative(new_alternatives, new_selection)
                        branched = True

        # If nothing has changed, selection is stable and we stop (only if a recursive call has not been launched)
        if not something_changed:
            if not branched:
                if not resoluteness:
                    selection.sort()
                    if selection not in all_selections:
                        all_selections.append(selection)
                else:
                    all_selections.append(selection)
        else:
            _select_next_alternative(alternatives, selection)

    try:
        max_size_selection = int(max_size_selection)
    except ValueError:
        raise ValueError("max_size_selection must be an integer.")

    if tie_breaking is None:
        tie_breaking = lexico_tie_breaking

    if initial_selection is not None:
        max_size_selection -= len(initial_selection)
    else:
        initial_selection = Selection(implicit_reject=True)

    initial_alternatives = {
        a for a in profile.alternatives if a not in initial_selection
    }
    all_selections = []
    thiele_score = thiele_score_class(max_size_selection)

    _select_next_alternative(initial_alternatives, initial_selection)

    if resoluteness:
        return all_selections[0]
    return all_selections

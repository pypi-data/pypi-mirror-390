from __future__ import annotations

from preflibtools.instances import CategoricalInstance, get_parsed_instance
from trivoting.election import TrichotomousMultiProfile, FrozenTrichotomousBallot

from trivoting.election.alternative import Alternative


def cat_preferences_to_frozen_trichotomous_ballot(
    pref: tuple[tuple[int]], alt_map: dict[int, Alternative]
) -> FrozenTrichotomousBallot:
    """
    Converts a categorical preference from PrefLib into a trichotomous ballot.

    The first category in the preference is treated as the set of approved alternatives.
    If a second category is present, it is treated as neutral and ignored in the ballot.
    If a third category is present, it is treated as the set of disapproved alternatives.

    Parameters
    ----------
    pref : tuple[tuple[int]]
        The categorical preferences, typically a tuple of up to 3 ranked groups of alternative IDs.
    alt_map : dict[int, Alternative]
        A mapping from PrefLib integer IDs to Alternative objects.

    Returns
    -------
    FrozenTrichotomousBallot
        The corresponding trichotomous ballot.

    Raises
    ------
    ValueError
        If the number of categories is not between 1 and 3.
    """
    if len(pref) == 0 or len(pref) > 3:
        raise ValueError(
            "Only categorical preferences between 1 and 3 categories can be converted to"
            f"a trichotomous ballot. Pref {pref} has {len(pref)} categories."
        )
    if len(pref) < 2:
        return FrozenTrichotomousBallot(approved=(alt_map[j] for j in pref[0]))
    return FrozenTrichotomousBallot(
        approved=(alt_map[j] for j in pref[0]),
        disapproved=(alt_map[j] for j in pref[-1]),
    )


def cat_instance_to_trichotomous_profile(
    cat_instance: CategoricalInstance,
) -> TrichotomousMultiProfile:
    """
    Converts a PrefLib CategoricalInstance into a trichotomous profile. The PrefLib instance should have 1, 2 or 3
    categories. If there is a single categories, it is assumed to represent the approved alternatives. If there are
    2 categories, it is assumed that they represent the approved and neutral alternatives. In case of 3 categories,
    the categories are assumed to represent approved, neutral and disapproved alternatives, in that order.

    Each ballot in the categorical instance is converted using
    `cat_preferences_to_trichotomous_ballot`.

    Parameters
    ----------
    cat_instance : CategoricalInstance
        A parsed categorical instance from PrefLib.

    Returns
    -------
    TrichotomousMultiProfile
        A multi-profile composed of trichotomous ballots.
    """
    if cat_instance.num_categories == 0 or cat_instance.num_categories > 3:
        raise ValueError(
            "Only categorical preferences between 1 and 3 categories can be converted to"
            f"a trichotomous profile. Categorical instance {cat_instance} has "
            f"{cat_instance.num_categories} categories."
        )

    alt_map = {j: Alternative(str(j)) for j in cat_instance.alternatives_name}
    profile = TrichotomousMultiProfile(alternatives=alt_map.values())

    for p, m in cat_instance.multiplicity.items():
        ballot = cat_preferences_to_frozen_trichotomous_ballot(p, alt_map)
        profile[ballot] = m

    return profile


def parse_preflib(file_path: str) -> TrichotomousMultiProfile:
    """
    Parses a PrefLib file and returns the corresponding trichotomous profile.

    The file is parsed using `preflibtools.get_parsed_instance`, and only
    categorical instances with 1–3 categories are supported.

    Parameters
    ----------
    file_path : str
        The file path to a PrefLib categorical instance.

    Returns
    -------
    TrichotomousMultiProfile
        A trichotomous multi-profile built from the given file.
    """

    instance = get_parsed_instance(file_path, autocorrect=True)
    if isinstance(instance, CategoricalInstance):
        return cat_instance_to_trichotomous_profile(instance)
    raise ValueError(
        f"PrefLib instances of type {type(instance)} cannot be converted to trichotomous profiles."
    )

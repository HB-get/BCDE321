import pytest

from zimp.domain.common.item_code import ItemCode
from zimp.domain.common.item_ids import (
    CARD_ITEM_IDS,
    ID_FOR_ITEM_CODE,
    IMPLEMENTED_ITEMS,
    ITEM_CODE_FOR_ID,
    RULEBOOK_ITEMS,
    item_id_for_card,
)
from zimp.domain.items.inventory import CONSUMABLE_EFFECTS, WEAPON_ATTACK


def test_every_implemented_item_is_a_rulebook_item() -> None:
    assert IMPLEMENTED_ITEMS <= set(RULEBOOK_ITEMS)


def test_implemented_items_match_what_the_inventory_actually_knows() -> None:
    known = set(WEAPON_ATTACK) | set(CONSUMABLE_EFFECTS)

    assert IMPLEMENTED_ITEMS == known


def test_rulebook_item_names_are_unique() -> None:
    assert len(set(RULEBOOK_ITEMS)) == len(RULEBOOK_ITEMS)


def test_every_mapped_card_produces_a_rulebook_item() -> None:
    """Guards the mapping as it is filled in, one card at a time."""
    assert set(CARD_ITEM_IDS.values()) <= set(RULEBOOK_ITEMS)


def test_no_two_cards_map_to_the_same_item() -> None:
    assert len(set(CARD_ITEM_IDS.values())) == len(CARD_ITEM_IDS)


def test_an_unmapped_card_is_refused_rather_than_guessed() -> None:
    unmapped = next(n for n in range(100) if n not in CARD_ITEM_IDS)

    with pytest.raises(ValueError, match=str(unmapped)):
        item_id_for_card(unmapped)


# Hayden's Game speaks ItemCode; the inventory speaks names. These two
# dictionaries are the whole translation, and they are the only place in
# Items that knows the other component's vocabulary.


def test_every_item_code_names_a_rulebook_item() -> None:
    assert set(ID_FOR_ITEM_CODE.values()) == set(RULEBOOK_ITEMS)


def test_every_rulebook_item_has_a_code() -> None:
    assert set(ITEM_CODE_FOR_ID) == set(RULEBOOK_ITEMS)


def test_nothing_is_the_only_code_without_a_name() -> None:
    """ItemCode.NONE marks an empty pocket, so it must not translate."""
    assert set(ID_FOR_ITEM_CODE) == set(ItemCode) - {ItemCode.NONE}


def test_translating_a_code_and_back_returns_the_same_code() -> None:
    for code, item_id in ID_FOR_ITEM_CODE.items():
        assert ITEM_CODE_FOR_ID[item_id] is code


def test_the_soda_keeps_its_inventory_name() -> None:
    """The two vocabularies disagree on this one item, and only this one."""
    assert ID_FOR_ITEM_CODE[ItemCode.SODA] == "can_of_soda"
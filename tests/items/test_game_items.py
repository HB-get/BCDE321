"""The seam between Hayden's Game and this inventory.

Game speaks `ItemCode` and reports failure as `ErrorCode | None` (or a
`Result` where a value has to come back). The inventory speaks item names
and refuses by raising `ValueError`. `GameItems` is the only place that
knows both, so neither component had to learn the other's vocabulary.
"""

import pytest

from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.item_code import ItemCode
from zimp.domain.items.game_items import GameItems
from zimp.domain.items.inventory import Inventory


def carrying(*item_ids: str) -> GameItems:
    inventory = Inventory()
    for item_id in item_ids:
        inventory.add(item_id)
    return GameItems(inventory)


# held_items


def test_an_empty_pocket_reads_as_nothing() -> None:
    assert GameItems().held_items() == (ItemCode.NONE, ItemCode.NONE)


def test_held_items_reports_codes_not_names() -> None:
    assert carrying("machete").held_items() == (ItemCode.MACHETE, ItemCode.NONE)


def test_both_pockets_are_reported() -> None:
    items = carrying("chainsaw", "can_of_soda")

    assert items.held_items() == (ItemCode.CHAINSAW, ItemCode.SODA)


# get_has_oil / get_has_instant_kill


def test_oil_is_reported_when_carried() -> None:
    assert carrying("oil").get_has_oil() is True


def test_oil_is_not_reported_when_absent() -> None:
    assert carrying("machete").get_has_oil() is False


def test_candle_and_gasoline_is_an_instant_kill() -> None:
    assert carrying("candle", "gasoline").get_has_instant_kill() is True


def test_candle_and_oil_is_also_an_instant_kill() -> None:
    assert carrying("candle", "oil").get_has_instant_kill() is True


def test_a_candle_alone_is_not_an_instant_kill() -> None:
    assert carrying("candle").get_has_instant_kill() is False


def test_fuel_without_a_candle_is_not_an_instant_kill() -> None:
    assert carrying("gasoline", "oil").get_has_instant_kill() is False


# attack_bonus


def test_attack_bonus_comes_back_as_a_successful_result() -> None:
    result = carrying("machete").attack_bonus(with_chainsaw=False)

    assert result.is_fail() is False
    assert result.get_data() == 2


def test_declining_the_chainsaw_uses_the_next_best_weapon() -> None:
    result = carrying("chainsaw", "machete").attack_bonus(with_chainsaw=False)

    assert result.get_data() == 2


def test_swinging_a_chainsaw_you_do_not_have_is_refused() -> None:
    result = carrying("machete").attack_bonus(with_chainsaw=True)

    assert result.is_fail() is True
    assert result.get_error_code() is ErrorCode.NO_CHAINSAW


def test_swinging_a_spent_chainsaw_is_refused() -> None:
    items = carrying("chainsaw")
    for _ in range(Inventory.CHAINSAW_BATTLES):
        items.record_battle()

    result = items.attack_bonus(with_chainsaw=True)

    assert result.get_error_code() is ErrorCode.NO_CHAINSAW


# the found-item pen


def test_a_found_item_is_not_carried_until_it_is_kept() -> None:
    items = GameItems()

    items.find_item(ItemCode.MACHETE)

    assert items.held_items() == (ItemCode.NONE, ItemCode.NONE)


def test_keeping_a_found_item_puts_it_in_a_pocket() -> None:
    items = GameItems()
    items.find_item(ItemCode.MACHETE)

    assert items.keep_found_item() is None
    assert items.held_items() == (ItemCode.MACHETE, ItemCode.NONE)


def test_keeping_nothing_is_refused() -> None:
    assert GameItems().keep_found_item() is ErrorCode.NO_FOUND_ITEM


def test_keeping_an_empty_find_is_refused() -> None:
    """`ItemCode.NONE` means the search turned up nothing, not an item."""
    items = GameItems()
    items.find_item(ItemCode.NONE)

    assert items.keep_found_item() is ErrorCode.NO_FOUND_ITEM
    assert items.held_items() == (ItemCode.NONE, ItemCode.NONE)


def test_keeping_an_item_with_no_pocket_free_is_refused() -> None:
    items = carrying("machete", "chainsaw")
    items.find_item(ItemCode.CANDLE)

    assert items.keep_found_item() is ErrorCode.NO_SPACE
    assert items.held_items() == (ItemCode.MACHETE, ItemCode.CHAINSAW)


def test_a_refused_item_can_still_be_kept_once_a_pocket_frees_up() -> None:
    """A full-pockets refusal must not throw the found item away."""
    items = carrying("machete", "chainsaw")
    items.find_item(ItemCode.CANDLE)
    items.keep_found_item()

    items.discard(0)

    assert items.keep_found_item() is None
    assert ItemCode.CANDLE in items.held_items()


def test_walking_away_from_a_found_item_forgets_it() -> None:
    items = GameItems()
    items.find_item(ItemCode.MACHETE)

    items.dont_take_item()

    assert items.keep_found_item() is ErrorCode.NO_FOUND_ITEM


# discard


def test_discarding_a_slot_empties_it() -> None:
    items = carrying("machete", "chainsaw")

    assert items.discard(1) is None
    assert items.held_items() == (ItemCode.MACHETE, ItemCode.NONE)


def test_discarding_an_empty_slot_is_refused() -> None:
    items = carrying("machete")

    assert items.discard(1) is ErrorCode.SLOT_EMPTY
    assert items.held_items() == (ItemCode.MACHETE, ItemCode.NONE)


# use


def test_using_a_soda_spends_it() -> None:
    items = carrying("can_of_soda")

    assert items.use(ItemCode.SODA) is None
    assert items.held_items() == (ItemCode.NONE, ItemCode.NONE)


def test_using_a_soda_you_do_not_have_is_refused() -> None:
    assert carrying("machete").use(ItemCode.SODA) is ErrorCode.NO_SODA


def test_using_gasoline_refuels_the_chainsaw() -> None:
    items = carrying("chainsaw", "gasoline")
    for _ in range(Inventory.CHAINSAW_BATTLES):
        items.record_battle()
    assert items.attack_bonus(with_chainsaw=True).is_fail() is True

    assert items.use(ItemCode.GASOLINE) is None

    assert items.attack_bonus(with_chainsaw=True).get_data() == 3


def test_using_gasoline_spends_it() -> None:
    items = carrying("chainsaw", "gasoline")

    items.use(ItemCode.GASOLINE)

    assert items.held_items() == (ItemCode.CHAINSAW, ItemCode.NONE)


def test_using_gasoline_you_do_not_have_is_refused() -> None:
    assert carrying("chainsaw").use(ItemCode.GASOLINE) is ErrorCode.NO_GASOLINE


def test_using_gasoline_without_a_chainsaw_is_refused_and_keeps_it() -> None:
    """Gasoline only does anything in a chainsaw. Pouring it on the ground
    would spend the can for nothing."""
    items = carrying("gasoline")

    assert items.use(ItemCode.GASOLINE) is ErrorCode.NO_CHAINSAW
    assert items.held_items() == (ItemCode.GASOLINE, ItemCode.NONE)


def test_using_oil_is_refused_and_keeps_it() -> None:
    """Oil is not a thing the player uses on its own."""
    items = carrying("oil")

    assert items.use(ItemCode.OIL) is not None
    assert items.held_items() == (ItemCode.OIL, ItemCode.NONE)


def test_using_a_weapon_is_refused_and_keeps_it() -> None:
    items = carrying("machete")

    assert items.use(ItemCode.MACHETE) is not None
    assert items.held_items() == (ItemCode.MACHETE, ItemCode.NONE)


# reset


def test_reset_empties_the_pockets() -> None:
    items = carrying("machete", "chainsaw")

    items.reset()

    assert items.held_items() == (ItemCode.NONE, ItemCode.NONE)


def test_reset_refills_the_chainsaw() -> None:
    items = carrying("chainsaw")
    for _ in range(Inventory.CHAINSAW_BATTLES):
        items.record_battle()

    items.reset()
    items.find_item(ItemCode.CHAINSAW)
    items.keep_found_item()

    assert items.attack_bonus(with_chainsaw=True).get_data() == 3


def test_reset_forgets_a_found_item() -> None:
    items = GameItems()
    items.find_item(ItemCode.MACHETE)

    items.reset()

    assert items.keep_found_item() is ErrorCode.NO_FOUND_ITEM


# record_battle


def test_battles_burn_chainsaw_fuel_through_the_adapter() -> None:
    items = carrying("chainsaw")

    items.record_battle()

    assert items.attack_bonus(with_chainsaw=True).get_data() == 3

    items.record_battle()

    assert items.attack_bonus(with_chainsaw=True).get_error_code() is (
        ErrorCode.NO_CHAINSAW
    )

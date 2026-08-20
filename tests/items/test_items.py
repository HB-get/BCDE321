import pytest

from zimp.domain.items.inventory import Inventory


def test_added_item_is_held() -> None:
    inventory = Inventory()

    inventory.add("machete")

    assert inventory.held == ["machete"]


def test_third_item_is_rejected_when_two_held() -> None:
    inventory = Inventory()
    inventory.add("machete")
    inventory.add("candle")

    with pytest.raises(ValueError):
        inventory.add("chainsaw")

    assert inventory.held == ["machete", "candle"]


def test_discarded_item_is_no_longer_held() -> None:
    inventory = Inventory()
    inventory.add("machete")
    inventory.add("candle")

    inventory.discard("machete")

    assert inventory.held == ["candle"]


def test_discarding_an_item_you_do_not_hold_is_rejected() -> None:
    inventory = Inventory()
    inventory.add("machete")

    with pytest.raises(ValueError, match="chainsaw"):
        inventory.discard("chainsaw")

    assert inventory.held == ["machete"]


def test_using_a_can_of_soda_gives_two_health() -> None:
    inventory = Inventory()
    inventory.add("can_of_soda")

    effect = inventory.use("can_of_soda")

    assert effect.health == 2


def test_a_used_consumable_is_spent() -> None:
    inventory = Inventory()
    inventory.add("can_of_soda")

    inventory.use("can_of_soda")

    assert inventory.held == []


def test_the_same_consumable_cannot_be_used_twice() -> None:
    inventory = Inventory()
    inventory.add("can_of_soda")
    inventory.use("can_of_soda")

    with pytest.raises(ValueError, match="can_of_soda"):
        inventory.use("can_of_soda")


def test_spending_a_consumable_frees_a_pocket() -> None:
    inventory = Inventory()
    inventory.add("can_of_soda")
    inventory.add("machete")

    inventory.use("can_of_soda")
    inventory.add("chainsaw")

    assert inventory.held == ["machete", "chainsaw"]



def test_holding_a_machete_gives_a_two_point_attack_bonus() -> None:
    inventory = Inventory()
    inventory.add("machete")

    assert inventory.attack_bonus() == 2


def test_empty_hands_give_no_attack_bonus() -> None:
    assert Inventory().attack_bonus() == 0


def test_a_carried_consumable_gives_no_attack_bonus() -> None:
    inventory = Inventory()
    inventory.add("can_of_soda")

    assert inventory.attack_bonus() == 0


def test_carrying_two_weapons_applies_only_the_stronger_one() -> None:
    inventory = Inventory()
    inventory.add("golf_club")
    inventory.add("machete")

    assert inventory.attack_bonus() == 2


def test_holding_a_chainsaw_gives_a_three_point_attack_bonus() -> None:
    inventory = Inventory()
    inventory.add("chainsaw")

    assert inventory.attack_bonus() == 3


def test_chainsaw_still_has_fuel_for_its_second_battle() -> None:
    inventory = Inventory()
    inventory.add("chainsaw")

    inventory.record_battle()

    assert inventory.attack_bonus() == 3


def test_chainsaw_gives_no_bonus_once_its_fuel_is_spent() -> None:
    inventory = Inventory()
    inventory.add("chainsaw")

    inventory.record_battle()
    inventory.record_battle()

    assert inventory.attack_bonus() == 0


def test_a_spent_chainsaw_is_still_carried() -> None:
    inventory = Inventory()
    inventory.add("chainsaw")

    inventory.record_battle()
    inventory.record_battle()

    assert inventory.held == ["chainsaw"]


def test_a_weaker_weapon_is_used_once_the_chainsaw_is_spent() -> None:
    inventory = Inventory()
    inventory.add("chainsaw")
    inventory.add("machete")

    inventory.record_battle()
    inventory.record_battle()

    assert inventory.attack_bonus() == 2


def test_using_an_item_you_do_not_hold_is_rejected() -> None:
    inventory = Inventory()
    inventory.add("machete")

    with pytest.raises(ValueError, match="can_of_soda"):
        inventory.use("can_of_soda")

    assert inventory.held == ["machete"]


def test_using_a_weapon_is_rejected() -> None:
    inventory = Inventory()
    inventory.add("machete")

    with pytest.raises(ValueError, match="machete"):
        inventory.use("machete")

    assert inventory.held == ["machete"]


def test_held_items_does_not_expose_the_inventory_to_mutation() -> None:
    inventory = Inventory()
    inventory.add("machete")

    inventory.held_items().append("chainsaw")

    assert inventory.held_items() == ["machete"]


# Three additions that let a slot-based, chainsaw-aware caller drive the
# same inventory the Tkinter shell drives. Existing behaviour is unchanged.


def test_discarding_by_slot_removes_that_slot() -> None:
    inventory = Inventory()
    inventory.add("machete")
    inventory.add("candle")

    inventory.discard_slot(1)

    assert inventory.held == ["machete"]


def test_discarding_by_slot_removes_the_right_one_of_two_identical_items() -> None:
    """Two machetes is a legal pocket, so a name cannot identify a slot."""
    inventory = Inventory()
    inventory.add("machete")
    inventory.add("chainsaw")

    inventory.discard_slot(0)

    assert inventory.held == ["chainsaw"]


def test_discarding_an_empty_slot_is_rejected() -> None:
    inventory = Inventory()
    inventory.add("machete")

    with pytest.raises(ValueError):
        inventory.discard_slot(1)

    assert inventory.held == ["machete"]


def test_refuelling_restores_a_spent_chainsaw() -> None:
    inventory = Inventory()
    inventory.add("chainsaw")
    for _ in range(Inventory.CHAINSAW_BATTLES):
        inventory.record_battle()
    assert inventory.attack_bonus() == 0

    inventory.refuel_chainsaw()

    assert inventory.attack_bonus() == 3


def test_declining_the_chainsaw_falls_back_to_the_next_weapon() -> None:
    inventory = Inventory()
    inventory.add("chainsaw")
    inventory.add("machete")

    assert inventory.attack_bonus(include_chainsaw=False) == 2


def test_declining_the_chainsaw_with_no_other_weapon_gives_nothing() -> None:
    inventory = Inventory()
    inventory.add("chainsaw")

    assert inventory.attack_bonus(include_chainsaw=False) == 0

from zimp.domain.items.inventory import Effect
from zimp.integration.game_controller import GameController
from zimp.support.fakes import FakeMovementGateway
from zimp.support.items.fake_items import FakeItemsGateway


def controller_with(items: FakeItemsGateway) -> GameController:
    """A controller whose only real collaborator under test is the inventory."""
    return GameController(FakeMovementGateway(), items)


def test_picking_up_an_item_reaches_the_inventory() -> None:
    items = FakeItemsGateway()

    message = controller_with(items).handle_pick_up_item("machete")

    assert items.calls == [("add", "machete")]
    assert message == "Picked up a machete."


def test_a_refused_pick_up_becomes_a_message_the_player_can_read() -> None:
    items = FakeItemsGateway()
    items.failure = ValueError("you are already carrying two items")

    message = controller_with(items).handle_pick_up_item("chainsaw")

    assert message == "Cannot pick up: you are already carrying two items"


def test_an_unavailable_inventory_does_not_crash_the_ui() -> None:
    items = FakeItemsGateway()
    items.failure = RuntimeError("dependency offline")

    assert controller_with(items).handle_pick_up_item("chainsaw").startswith(
        "Cannot pick up:"
    )


def test_using_a_consumable_reports_its_effect_to_the_player() -> None:
    items = FakeItemsGateway(effect=Effect(health=2))

    message = controller_with(items).handle_use_item("can_of_soda")

    assert items.calls == [("use", "can_of_soda")]
    assert message == "Used a can_of_soda. Health +2."


def test_using_a_weapon_is_refused_in_words_the_player_can_read() -> None:
    items = FakeItemsGateway()
    items.failure = ValueError("a machete is not something you can use")

    message = controller_with(items).handle_use_item("machete")

    assert message == "Cannot use: a machete is not something you can use"


def test_discarding_an_item_reaches_the_inventory() -> None:
    items = FakeItemsGateway(held=["machete"])

    message = controller_with(items).handle_discard_item("machete")

    assert items.calls == [("discard", "machete")]
    assert message == "Dropped a machete."


def test_a_refused_discard_becomes_a_message_the_player_can_read() -> None:
    items = FakeItemsGateway()
    items.failure = ValueError("you are not carrying a machete")

    assert (
        controller_with(items).handle_discard_item("machete")
        == "Cannot drop: you are not carrying a machete"
    )


def test_an_effect_that_changes_both_health_and_attack_reports_both() -> None:
    items = FakeItemsGateway(effect=Effect(health=-1, attack=1))

    message = controller_with(items).handle_use_item("mystery_brew")

    assert message == "Used a mystery_brew. Health -1. Attack +1."


def test_the_controller_reports_what_the_player_is_carrying() -> None:
    items = FakeItemsGateway(held=["machete", "can_of_soda"])

    assert controller_with(items).held_items() == ["machete", "can_of_soda"]


def test_an_unavailable_inventory_reports_nothing_carried_rather_than_crashing() -> None:
    items = FakeItemsGateway()
    items.held_items = _raise_offline

    assert controller_with(items).held_items() == []


def _raise_offline() -> list[str]:
    raise RuntimeError("dependency offline")

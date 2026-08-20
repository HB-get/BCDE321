from zimp.integration.game_controller import GameController
from zimp.support.fakes import FakeMovementGateway


def test_controller_calls_dependency_across_boundary() -> None:
    fake = FakeMovementGateway("Integrated successfully.")

    result = GameController(fake).handle_move("east")

    assert result == "Integrated successfully."
    assert fake.calls == ["east"]


def test_controller_maps_expected_failure_to_visible_message() -> None:
    fake = FakeMovementGateway()
    fake.failure = ValueError("blocked")

    assert GameController(fake).handle_move("north") == "Cannot move: blocked"


def test_controller_maps_unavailable_component_to_visible_message() -> None:
    fake = FakeMovementGateway()
    fake.failure = RuntimeError("dependency offline")

    assert GameController(fake).handle_move("north").startswith("Cannot move:")



def test_controller_normalises_movement_direction() -> None:
    fake = FakeMovementGateway("Moved north.")

    result = GameController(fake).handle_move(" NORTH ")

    assert result == "Moved north."
    assert fake.calls == ["north"]


def test_controller_rejects_invalid_direction() -> None:
    fake = FakeMovementGateway()

    result = GameController(fake).handle_move("banana")

    assert result == "Cannot move: invalid direction 'banana'."
    assert fake.calls == []

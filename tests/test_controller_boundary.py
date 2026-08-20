from zimp.integration.game_controller import GameController
from zimp.support.fakes import FakeMovementGateway
from zimp.support.items.fake_items import FakeItemsGateway


def test_controller_calls_dependency_across_boundary() -> None:
    fake = FakeMovementGateway("Integrated successfully.")

    result = GameController(fake, FakeItemsGateway()).handle_move("east")

    assert result == "Integrated successfully."
    assert fake.calls == ["east"]


def test_controller_maps_expected_failure_to_visible_message() -> None:
    fake = FakeMovementGateway()
    fake.failure = ValueError("blocked")

    assert GameController(fake, FakeItemsGateway()).handle_move("north") == "Cannot move: blocked"


def test_controller_maps_unavailable_component_to_visible_message() -> None:
    fake = FakeMovementGateway()
    fake.failure = RuntimeError("dependency offline")

    assert GameController(fake, FakeItemsGateway()).handle_move("north").startswith("Cannot move:")

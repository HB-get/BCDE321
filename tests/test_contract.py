from zimp.domain.basic_movement import BasicMovement
from zimp.domain.contracts import MovementGateway
from zimp.domain.game_state.game_state import GameState
from zimp.support.fakes import FakeMovementGateway


def test_real_and_fake_satisfy_movement_contract() -> None:
    assert isinstance(BasicMovement(GameState()), MovementGateway)
    assert isinstance(FakeMovementGateway(), MovementGateway)

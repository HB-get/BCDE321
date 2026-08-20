from zimp.domain.common.contract_movement import MovementContract
from zimp.domain.movement.game_map import GameMap


def test_game_map_fits_movement_contract() -> None:
    assert isinstance(GameMap(), MovementContract)

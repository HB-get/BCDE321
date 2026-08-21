from zimp.domain.common.contract_movement import ContractMovement
from zimp.domain.map.game_map import GameMap


class TestContractMovement():
    def test_game_map_fits_movement_contract(self) -> None:
        assert isinstance(GameMap(), ContractMovement)

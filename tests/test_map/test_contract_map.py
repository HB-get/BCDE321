from zimp.domain.common.contract_map import ContractMap
from zimp.domain.map.game_map import GameMap


class TestContractMap():
    def test_game_map_fits_map_contract(self) -> None:
        assert isinstance(GameMap(), ContractMap)

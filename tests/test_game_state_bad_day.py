import pytest

from zimp.domain.game_state.game_state import GameState
from zimp.domain.game_state.mode import Mode
from zimp.domain.common.error_code import ErrorCode


class TestGameStateBadDay:

    @pytest.fixture
    def gs(self) -> GameState:
        return GameState()

    def test_check_loss_by_health(self, gs: GameState):
        gs.health = 0
        assert gs.check_is_lost()
        assert gs.mode == Mode.LOST

    def test_check_loss_by_time(self, gs: GameState):
        gs.time_ran_out = True
        assert gs.check_is_lost()
        assert gs.mode == Mode.LOST

    def test_advance_time_time_out(self, gs: GameState):
        gs.hour = 2
        gs.advance_time()
        assert gs.time_ran_out

    def test_change_hp_bounds_negative(self, gs: GameState):
        gs.health = 2
        gs.change_hp(-5)
        assert gs.health == 0

    def test_cower_failure_already_cowered(self, gs: GameState):
        gs.mode = Mode.EVENTS_FINISHED
        gs.cowered_this_turn = True
        result = gs.cower()
        assert result.is_fail()
        assert result.get_error_code() == ErrorCode.ALREADY_COWERED

    def test_cower_failure_wrong_mode(self, gs: GameState):
        gs.mode = Mode.NONE
        gs.cowered_this_turn = False
        result = gs.cower()
        assert result.is_fail()
        assert result.get_error_code() == ErrorCode.ALREADY_COWERED

    def test_bury_totem_without_having_it(self, gs: GameState):
        gs.bury_totem()
        assert not gs.buried_totem

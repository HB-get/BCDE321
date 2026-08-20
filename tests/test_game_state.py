import pytest
from zimp.domain.common.mode import Mode
from zimp.domain.game_state import GameState


# RESET

def test_reset_restores_initial_values():
    state = GameState(
        last_move="north",
        turn_number=5,
        mode=Mode.COMBAT,
        attack=3,
        health=2,
        hour=2,
        has_totem=True,
        buried_totem=True,
        cowered_this_turn=True,
        time_ran_out=True,
    )

    state.reset()

    assert state.last_move is None
    assert state.turn_number == 0
    assert state.mode is Mode.NONE
    assert state.attack == 1
    assert state.health == 6
    assert state.hour == 0
    assert not state.has_totem
    assert not state.buried_totem
    assert not state.cowered_this_turn
    assert not state.time_ran_out


# TIME

def test_advance_time_increases_hour():
    state = GameState()
    state.advance_time(1)
    assert state.hour == 1

def test_advance_time_sets_time_ran_out_when_hour_reaches_11pm():
    state = GameState(hour=1)
    state.advance_time(1)
    assert state.hour == 2
    assert state.time_ran_out is True


# HP CHANGES

def test_change_hp_heals_with_positive_values():
    state = GameState(health=3)
    state.change_hp(2)
    assert state.health == 5

def test_change_hp_damages_with_negative_values():
    state = GameState(health=5)
    state.change_hp(-3)
    assert state.health == 2

def test_change_hp_never_goes_below_zero():
    state = GameState(health=1)
    state.change_hp(-10)
    assert state.health == 0


# TOTEM

def test_take_totem_sets_flag():
    state = GameState()
    state.take_totem()
    assert state.has_totem is True

def test_bury_totem_only_works_if_player_has_totem():
    state = GameState(has_totem=False)
    state.bury_totem()
    assert not state.buried_totem

def test_bury_totem_sets_buried_and_removes_totem():
    state = GameState(has_totem=True)
    state.bury_totem()
    assert state.buried_totem is True
    assert state.has_totem is False


# COWERING

def test_cower_heals_and_signals_discard():
    state = GameState(health=3)
    healed, discard = state.cower()
    assert healed == 3
    assert discard is True
    assert state.health == 6
    assert state.cowered_this_turn is True

def test_cannot_cower_twice_in_one_turn():
    state = GameState()
    state.cower()
    healed, discard = state.cower()
    assert healed == 0
    assert discard is False


# WIN / LOSS CONDITIONS

def test_is_won_true_when_totem_buried_and_alive():
    state = GameState(buried_totem=True, health=5)
    assert state.is_won() is True

def test_is_won_false_if_not_buried():
    state = GameState(buried_totem=False, health=5)
    assert not state.is_won()

def test_is_lost_true_when_health_zero():
    state = GameState(health=0)
    assert state.is_lost() is True

def test_is_lost_true_when_time_ran_out():
    state = GameState(time_ran_out=True)
    assert state.is_lost() is True

def test_is_lost_true_when_mode_is_lost():
    state = GameState(mode=Mode.LOST)
    assert state.is_lost() is True

def test_is_lost_false_when_alive_and_time_ok():
    state = GameState(health=5, time_ran_out=False)
    assert not state.is_lost()


# MODE SETTING

def test_set_mode_changes_mode():
    state = GameState()
    state.set_mode(Mode.COMBAT)
    assert state.mode is Mode.COMBAT

def test_set_mode_rejects_invalid_values():
    state = GameState()
    with pytest.raises(ValueError):
        state.set_mode("INVALID")


# CHECK WIN / LOSS

def test_check_win_loss_sets_mode_to_won():
    state = GameState(buried_totem=True, health=5)
    mode = state.check_win_loss()
    assert mode is Mode.WON
    assert state.mode is Mode.WON

def test_check_win_loss_sets_mode_to_lost():
    state = GameState(health=0)
    mode = state.check_win_loss()
    assert mode is Mode.LOST
    assert state.mode is Mode.LOST

def test_check_win_loss_does_not_override_existing_terminal_mode():
    state = GameState(mode=Mode.WON, buried_totem=False, health=0)
    mode = state.check_win_loss()
    assert mode is Mode.WON  # stays WON


# GETTERS

def test_get_hp_returns_string():
    state = GameState(health=5)
    assert state.get_hp() == " HP: 5"

def test_get_attack_returns_string():
    state = GameState(attack=3)
    assert state.get_attack() == "ATK: 3"

def test_get_stats_returns_string():
    state = GameState(health=6, attack=1, hour=0, buried_totem=False)
    assert "HP: 6" in state.get_stats()
    assert "ATK: 1" in state.get_stats()
    assert "Hour: 0" in state.get_stats()

def test_get_time_returns_string():
    state = GameState(hour=1)
    assert state.get_time() == "Hour: 1"

def test_has_got_totem_returns_boolean():
    state = GameState(has_totem=True)
    assert state.has_got_totem() is True
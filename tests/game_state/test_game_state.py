import pytest

from zimp.domain.game_state.game_state import GameState
from zimp.domain.game_state.mode import Mode
from zimp.domain.common.tile_effect import TileEffect
from zimp.domain.common.dev_card import CardEffect, CardEffectType
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.result import Result


@pytest.fixture
def gs() -> GameState:
    return GameState()

def test_initial_state_defaults(gs: GameState):
    assert gs.mode == Mode.NONE
    assert gs.health == 6
    assert gs.hour == 0
    assert gs.has_totem is False
    assert gs.buried_totem is False
    assert gs.cowered_this_turn is False
    assert gs.time_ran_out is False
    assert gs.in_combat is False
    assert gs.num_zombies == 0
    assert gs.have_ended_turn is False


def test_reset_restores_defaults(gs: GameState):
    gs.health = 2
    gs.hour = 2
    gs.has_totem = True
    gs.buried_totem = True
    gs.cowered_this_turn = True
    gs.time_ran_out = True
    gs.in_combat = True
    gs.num_zombies = 5
    gs.have_ended_turn = True

    gs.reset()

    assert gs.mode == Mode.NONE
    assert gs.health == 6
    assert gs.hour == 0
    assert not gs.has_totem
    assert not gs.buried_totem
    assert not gs.cowered_this_turn
    assert not gs.time_ran_out
    assert not gs.in_combat
    assert gs.num_zombies == 0
    assert not gs.have_ended_turn


def test_getters(gs: GameState):
    assert gs.get_hp() == gs.health
    assert gs.get_time() == gs.hour


def test_mode_queries(gs: GameState):
    gs.mode = Mode.NONE
    assert gs.get_can_move()
    gs.mode = Mode.MOVE
    assert gs.get_is_moving()
    gs.mode = Mode.COMBAT
    assert gs.get_can_attack()
    assert gs.get_can_flee()
    gs.mode = Mode.ZOMBIE_DOOR
    assert gs.get_is_zombie_door()
    gs.mode = Mode.ITEM_SEARCH
    assert gs.get_is_searching_item()
    gs.mode = Mode.ITEM_FOUND
    assert gs.get_has_found_item()
    gs.mode = Mode.EVENTS_FINISHED
    assert gs.get_can_end_turn()
    gs.mode = Mode.DEV_CARD
    assert gs.get_is_doing_events()


def test_check_win_and_loss_transitions(gs: GameState):
    # not won initially
    assert not gs.check_is_won()
    # set up winning conditions
    gs.buried_totem = True
    gs.mode = Mode.NONE
    gs.health = 1
    gs.time_ran_out = False
    assert gs.check_is_won()
    assert gs.mode == Mode.WON

    # losing by health
    gs.reset()
    gs.health = 0
    assert gs.check_is_lost()
    assert gs.mode == Mode.LOST

    # losing by time
    gs.reset()
    gs.time_ran_out = True
    assert gs.check_is_lost()
    assert gs.mode == Mode.LOST


def test_advance_time_and_time_out(gs: GameState):
    # default start 0, max time is 2 in implementation
    assert gs.hour == 0
    gs.advance_time()
    assert gs.hour == 1
    gs.advance_time()
    assert gs.hour == 2
    # advancing beyond max sets time_ran_out
    gs.advance_time()
    assert gs.time_ran_out is True


def test_start_and_end_move(gs: GameState):
    gs.start_move()
    assert gs.mode == Mode.MOVE
    gs.end_move()
    assert gs.mode == Mode.DEV_CARD


def test_zombie_door_and_confirm(gs: GameState):
    gs.start_zombie_door()
    assert gs.mode == Mode.ZOMBIE_DOOR
    gs.confirm_zombie_door()
    assert gs.in_combat is True
    assert gs.mode == Mode.COMBAT
    assert gs.num_zombies == 3  # constant in implementation


def test_searching_item_transitions(gs: GameState):
    gs.start_searching_item()
    assert gs.mode == Mode.ITEM_SEARCH
    gs.end_searching_item()
    assert gs.mode == Mode.EVENTS_FINISHED
    gs.find_item()
    assert gs.mode == Mode.ITEM_FOUND
    gs.end_found_item()
    assert gs.mode == Mode.EVENTS_FINISHED


def test_change_hp_bounds(gs: GameState):
    gs.health = 2
    gs.change_hp(-5)
    assert gs.health == 0  # cannot go below zero
    gs.change_hp(10)
    assert gs.health == 10  # no upper bound enforced


def test_apply_card_effect_health(gs: GameState):
    effect = CardEffect(CardEffectType.HEALTH, 2)
    gs.apply_card_effect(effect)
    assert gs.health == 8
    assert gs.mode == Mode.EVENTS_FINISHED


def test_apply_card_effect_zombies(gs: GameState):
    effect = CardEffect(CardEffectType.ZOMBIES, 4)
    gs.apply_card_effect(effect)
    assert gs.in_combat is True
    assert gs.mode == Mode.COMBAT
    assert gs.num_zombies == 4


def test_apply_card_effect_item_and_none(gs: GameState):
    effect_item = CardEffect(CardEffectType.ITEM, 0)
    gs.apply_card_effect(effect_item)
    assert gs.mode == Mode.ITEM_SEARCH

    gs.reset()
    effect_none = CardEffect(CardEffectType.NONE, 0)
    gs.apply_card_effect(effect_none)
    assert gs.mode == Mode.EVENTS_FINISHED


def test_combat_attack_damage_and_limits(gs: GameState):
    gs.start_combat(5)
    # base attack is 1 in implementation; attack_bonus 0 => damage = 5 - 1 = 4 (max 4)
    gs.attack(attack_bonus=0, instant_kill=False)
    assert gs.in_combat is False
    assert gs.mode == Mode.EVENTS_FINISHED
    # health decreased by up to 4
    assert gs.health == 2

    # instant kill should not reduce health
    gs.start_combat(5)
    prev_hp = gs.health
    gs.attack(attack_bonus=0, instant_kill=True)
    assert gs.health == prev_hp
    assert gs.in_combat is False


def test_flee_with_and_without_oil(gs: GameState):
    gs.start_combat(3)
    prev_hp = gs.health
    gs.flee(with_oil=False)
    assert gs.in_combat is False
    assert gs.health == prev_hp - 1

    gs.start_combat(3)
    prev_hp = gs.health
    gs.flee(with_oil=True)
    assert gs.health == prev_hp  # no damage when using oil


def test_cower_success_and_failure(gs: GameState):
    # cower only allowed when mode == EVENTS_FINISHED and not already cowered
    gs.mode = Mode.EVENTS_FINISHED
    gs.cowered_this_turn = False
    result = gs.cower()
    assert isinstance(result, Result)
    assert not result.is_fail()
    assert gs.cowered_this_turn is True
    assert gs.health == 9  # healed by 3

    # second cower in same turn fails
    res2 = gs.cower()
    assert res2.is_fail()
    assert res2.get_error_code() == ErrorCode.ALREADY_COWERED

    # cower when not in EVENTS_FINISHED fails
    gs.reset()
    gs.mode = Mode.NONE
    gs.cowered_this_turn = False
    res3 = gs.cower()
    assert res3.is_fail()
    assert res3.get_error_code() == ErrorCode.ALREADY_COWERED


def test_totem_take_and_bury(gs: GameState):
    gs.take_totem()
    assert gs.has_totem is True
    gs.bury_totem()
    assert gs.buried_totem is True

    # bury without totem should not set buried_totem
    gs.reset()
    gs.bury_totem()
    assert gs.buried_totem is False


def test_drink_soda(gs: GameState):
    prev = gs.health
    gs.drink_soda()
    assert gs.health == prev + 2


def test_do_end_turn_effects(gs: GameState):
    # HEALTH tile effect
    gs.do_end_turn_effect(TileEffect.HEALTH)
    assert gs.have_ended_turn is True
    # HEALTH increases by tile heal amount (1)
    assert gs.health == 7

    # SEARCH effect sets mode to ITEM_SEARCH
    gs.reset()
    gs.do_end_turn_effect(TileEffect.SEARCH)
    assert gs.mode == Mode.ITEM_SEARCH

    # FIND_TOTEM sets mode to DEV_CARD and gives totem
    gs.reset()
    gs.do_end_turn_effect(TileEffect.FIND_TOTEM)
    assert gs.mode == Mode.DEV_CARD
    assert gs.has_totem is True

    # BURY_TOTEM sets mode to DEV_CARD and buries if has_totem
    gs.reset()
    gs.take_totem()
    gs.do_end_turn_effect(TileEffect.BURY_TOTEM)
    assert gs.mode == Mode.DEV_CARD
    assert gs.buried_totem is True


def test_start_new_turn_resets_flags(gs: GameState):
    gs.have_ended_turn = True
    gs.cowered_this_turn = True
    gs.mode = Mode.DEV_CARD
    gs.start_new_turn()
    assert gs.have_ended_turn is False
    assert gs.cowered_this_turn is False
    assert gs.mode == Mode.NONE
import pytest

from zimp.domain.game_state.game_state import GameState
from zimp.domain.game_state.mode import Mode
from zimp.domain.common.tile_effect import TileEffect
from zimp.domain.common.dev_card import CardEffect, CardEffectType


class TestGameStateGoodDay:

    @pytest.fixture
    def gs(self) -> GameState:
        return GameState()

    def test_initial_state_defaults(self, gs: GameState):
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

    def test_reset_restores_defaults(self, gs: GameState):
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

    def test_getters(self, gs: GameState):
        assert gs.get_hp() == gs.health
        assert gs.get_time() == gs.hour

    def test_mode_queries(self, gs: GameState):
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

    def test_check_win_transition(self, gs: GameState):
        gs.buried_totem = True
        gs.mode = Mode.NONE
        gs.health = 1
        gs.time_ran_out = False
        assert gs.check_is_won()
        assert gs.mode == Mode.WON

    def test_advance_time_normal(self, gs: GameState):
        assert gs.hour == 0
        gs.advance_time()
        assert gs.hour == 1
        gs.advance_time()
        assert gs.hour == 2

    def test_start_and_end_move(self, gs: GameState):
        gs.start_move()
        assert gs.mode == Mode.MOVE
        gs.end_move()
        assert gs.mode == Mode.DEV_CARD

    def test_zombie_door_and_confirm(self, gs: GameState):
        gs.start_zombie_door()
        assert gs.mode == Mode.ZOMBIE_DOOR
        gs.confirm_zombie_door()
        assert gs.in_combat
        assert gs.mode == Mode.COMBAT
        assert gs.num_zombies == 3

    def test_searching_item_transitions(self, gs: GameState):
        gs.start_searching_item()
        assert gs.mode == Mode.ITEM_SEARCH
        gs.end_searching_item()
        assert gs.mode == Mode.EVENTS_FINISHED
        gs.find_item()
        assert gs.mode == Mode.ITEM_FOUND
        gs.end_found_item()
        assert gs.mode == Mode.EVENTS_FINISHED

    def test_change_hp_bounds_positive(self, gs: GameState):
        gs.change_hp(10)
        assert gs.health == 16

    def test_apply_card_effect_health(self, gs: GameState):
        effect = CardEffect(CardEffectType.HEALTH, 2)
        gs.apply_card_effect(effect)
        assert gs.health == 8
        assert gs.mode == Mode.EVENTS_FINISHED

    def test_apply_card_effect_zombies(self, gs: GameState):
        effect = CardEffect(CardEffectType.ZOMBIES, 4)
        gs.apply_card_effect(effect)
        assert gs.in_combat
        assert gs.mode == Mode.COMBAT
        assert gs.num_zombies == 4

    def test_apply_card_effect_item(self, gs: GameState):
        effect_item = CardEffect(CardEffectType.ITEM, 0)
        gs.apply_card_effect(effect_item)
        assert gs.mode == Mode.ITEM_SEARCH

    def test_apply_card_effect_none(self, gs: GameState):
        effect_none = CardEffect(CardEffectType.NONE, 0)
        gs.apply_card_effect(effect_none)
        assert gs.mode == Mode.EVENTS_FINISHED

    def test_combat_attack_normal(self, gs: GameState):
        gs.start_combat(5)
        gs.attack(attack_bonus=0, instant_kill=False)
        assert not gs.in_combat
        assert gs.mode == Mode.EVENTS_FINISHED
        assert gs.health == 2

    def test_combat_attack_instant_kill(self, gs: GameState):
        gs.start_combat(5)
        prev_hp = gs.health
        gs.attack(attack_bonus=0, instant_kill=True)
        assert gs.health == prev_hp
        assert not gs.in_combat

    def test_flee_without_oil(self, gs: GameState):
        gs.start_combat(3)
        prev_hp = gs.health
        gs.flee(with_oil=False)
        assert not gs.in_combat
        assert gs.health == prev_hp - 1

    def test_flee_with_oil(self, gs: GameState):
        gs.start_combat(3)
        prev_hp = gs.health
        gs.flee(with_oil=True)
        assert gs.health == prev_hp

    def test_cower_success(self, gs: GameState):
        gs.mode = Mode.EVENTS_FINISHED
        gs.cowered_this_turn = False
        result = gs.cower()
        assert not result.is_fail()
        assert gs.cowered_this_turn
        assert gs.health == 9

    def test_totem_take_and_bury(self, gs: GameState):
        gs.take_totem()
        assert gs.has_totem
        gs.bury_totem()
        assert gs.buried_totem

    def test_drink_soda(self, gs: GameState):
        prev = gs.health
        gs.drink_soda()
        assert gs.health == prev + 2

    def test_do_end_turn_effects(self, gs: GameState):
        gs.do_end_turn_effect(TileEffect.HEALTH)
        assert gs.have_ended_turn
        assert gs.health == 7

        gs.reset()
        gs.do_end_turn_effect(TileEffect.SEARCH)
        assert gs.mode == Mode.ITEM_SEARCH

        gs.reset()
        gs.do_end_turn_effect(TileEffect.FIND_TOTEM)
        assert gs.mode == Mode.DEV_CARD
        assert gs.has_totem

        gs.reset()
        gs.take_totem()
        gs.do_end_turn_effect(TileEffect.BURY_TOTEM)
        assert gs.mode == Mode.DEV_CARD
        assert gs.buried_totem

    def test_start_new_turn_resets_flags(self, gs: GameState):
        gs.have_ended_turn = True
        gs.cowered_this_turn = True
        gs.mode = Mode.DEV_CARD
        gs.start_new_turn()
        assert not gs.have_ended_turn
        assert not gs.cowered_this_turn
        assert gs.mode == Mode.NONE

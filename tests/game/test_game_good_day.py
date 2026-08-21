import pytest

from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.item_code import ItemCode
from zimp.domain.common.result import Result
from zimp.domain.game.game import Game

from tests.game.game_fakes import (
    FakeEvents,
    FakeGameState,
    FakeItems,
    FakeMovement,
)

class TestGameGoodDay:

    @pytest.fixture
    def game(self):
        state = FakeGameState()
        movement = FakeMovement()
        items = FakeItems()
        events = FakeEvents()

        game = Game(
            state=state,
            movement=movement,
            items=items,
            events=events,
        )

        return game, state, movement, items, events


    # -----------------------------------------------------------------------------------------------------------
    # reset
    # -----------------------------------------------------------------------------------------------------------

    def test_game_constructor_resets_all_components(self, game):
        _, state, movement, items, events = game

        assert state.reset_calls == 1
        assert movement.reset_calls == 1
        assert items.reset_calls == 1
        assert events.reset_calls == 1

    def test_reset_resets_all_components(self, game):
        game, state, movement, items, events = game

        game.reset()

        assert state.reset_calls == 2
        assert movement.reset_calls == 2
        assert items.reset_calls == 2
        assert events.reset_calls == 2


    # -----------------------------------------------------------------------------------------------------------
    # move_player
    # -----------------------------------------------------------------------------------------------------------

    def test_move_player_delegates_to_movement(self, game):
        game, _, movement, _, _ = game

        result = game.move_player(Direction.NORTH)

        assert result is None
        assert movement.move_calls == [Direction.NORTH]


    def test_move_player_enters_placement_mode_after_unknown_tile(self, game):
        game, state, movement, _, events = game

        movement.placement_mode_on = True

        result = game.move_player(Direction.NORTH)

        assert result is None
        assert state.start_move_calls == 1
        assert events.draw_event_calls == []


    def test_move_player_draws_event_after_known_tile(self, game):
        game, state, movement, _, events = game

        movement.placement_mode_on = False

        result = game.move_player(Direction.NORTH)

        assert result is None
        assert state.start_move_calls == 0
        assert events.draw_event_calls == [state.time]


    # -----------------------------------------------------------------------------------------------------------
    # _draw_event_card / _do_post_event_checks
    # -----------------------------------------------------------------------------------------------------------

    def test_event_card_effect_is_applied(self, game):
        #This "assumes" moving to a known tile
        game, state, _, _, events = game

        events.draw_event_result = Result.success("zombie attack")

        game.move_player(Direction.NORTH)

        assert state.apply_card_effect_calls == ["zombie attack"]


    def test_shuffled_event_advances_time(self, game):
        game, state, _, _, events = game

        events.draw_event_result = Result.success("event")
        events.draw_event_shuffled = True

        game.move_player(Direction.NORTH)

        assert state.advance_time_calls == 1


    def test_non_shuffled_event_does_not_advance_time(self, game):
        game, state, _, _, events = game

        events.draw_event_shuffled = False

        game.move_player(Direction.NORTH)

        assert state.advance_time_calls == 0


    def test_post_event_check_starts_zombie_door_first(self, game):
        game, state, movement, _, _ = game

        state.can_end_turn = True
        movement.needs_zombie_door = True
        state.has_ended_turn = True

        game.move_player(Direction.NORTH)

        assert movement.need_zombie_door_calls == 1
        assert state.start_zombie_door_calls == 1
        assert state.start_new_turn_calls == 0


    def test_post_event_check_starts_new_turn_when_no_zombie_door(self, game):
        game, state, movement, _, _ = game

        state.can_end_turn = True
        movement.needs_zombie_door = False
        state.has_ended_turn = True

        game.move_player(Direction.NORTH)

        assert state.start_zombie_door_calls == 0
        assert state.start_new_turn_calls == 1

    # -----------------------------------------------------------------------------------------------------------
    # rotate_tile
    # -----------------------------------------------------------------------------------------------------------

    def test_rotate_tile_delegates_to_movement(self, game):
        game, state, movement, _, _ = game

        state.is_moving = True

        result = game.rotate_tile()

        assert result is None
        assert movement.rotate_placement_tile_calls == 1


    # -----------------------------------------------------------------------------------------------------------
    # place_tile
    # -----------------------------------------------------------------------------------------------------------

    def test_place_tile_locks_tile_and_ends_move(self, game):
        game, state, movement, _, _ = game

        state.is_moving = True
        movement.lock_placement_tile_result = None

        result = game.place_tile()

        assert result is None
        assert movement.lock_placement_tile_calls == 1
        assert state.end_move_calls == 1


    def test_place_tile_draws_event_after_successful_lock(self, game):
        game, state, movement, _, events = game

        state.is_moving = True
        movement.lock_placement_tile_result = None

        game.place_tile()

        assert state.end_move_calls == 1
        assert events.draw_event_calls == [state.time]


    # -----------------------------------------------------------------------------------------------------------
    # pick_zombie_door
    # -----------------------------------------------------------------------------------------------------------

    def test_pick_zombie_door_delegates_to_movement(self, game):
        game, state, movement, _, _ = game

        state.is_zombie_door = True

        result = game.pick_zombie_door(Direction.EAST)

        assert result is None
        assert movement.create_zombie_door_calls == [Direction.EAST]
        assert state.confirm_zombie_door_calls == 1


    # -----------------------------------------------------------------------------------------------------------
    # attack
    # -----------------------------------------------------------------------------------------------------------

    def test_attack_uses_item_attack_bonus(self, game):
        game, state, _, items, _ = game

        items.attack_bonus_result = Result.success(3)

        result = game.attack()

        assert result is None
        assert items.attack_bonus_calls == [False]
        assert state.attack_calls == [(3, False)]
        assert items.record_battle_calls == 1


    def test_attack_passes_chainsaw_flag_to_items(self, game):
        game, state, _, items, _ = game

        items.attack_bonus_result = Result.success(4)

        result = game.attack(use_chainsaw=True)

        assert result is None
        assert items.attack_bonus_calls == [True]
        assert state.attack_calls == [(4, False)]


    def test_attack_with_instant_kill_discards_both_required_items(self, game):
        game, state, _, items, _ = game

        items.instant_kill_available = True
        items.attack_bonus_result = Result.success(0)

        result = game.attack(instant_kill=True)

        assert result is None
        assert items.discard_calls == [0, 1]
        assert state.attack_calls == [(0, True)]
        assert items.record_battle_calls == 1


    def test_attack_post_event_checks_are_performed(self, game):
        game, state, movement, items, _ = game

        items.attack_bonus_result = Result.success(2)
        state.can_end_turn = True
        movement.needs_zombie_door = True

        game.attack()

        assert state.start_zombie_door_calls == 1


    # -----------------------------------------------------------------------------------------------------------
    # flee
    # -----------------------------------------------------------------------------------------------------------


    def test_flee_delegates_to_movement(self, game):
        game, state, movement, _, _ = game

        result = game.flee(Direction.NORTH)

        assert result is None
        assert movement.flee_calls == [Direction.NORTH]
        assert state.flee_calls == [False]


    def test_flee_with_oil_uses_oil_after_success(self, game):
        game, state, movement, items, _ = game

        result = game.flee(Direction.SOUTH, with_oil=True)

        assert result is None
        assert movement.flee_calls == [Direction.SOUTH]
        assert state.flee_calls == [True]
        assert items.use_calls == [ItemCode.OIL]


    def test_flee_without_oil_does_not_use_oil(self, game):
        game, _, _, items, _ = game

        result = game.flee(Direction.SOUTH, with_oil=False)

        assert result is None
        assert items.use_calls == []


    # -----------------------------------------------------------------------------------------------------------
    # perform_search_for_item
    # -----------------------------------------------------------------------------------------------------------


    def test_search_for_item_draws_item(self, game):
        game, state, _, items, events = game

        state.is_searching_item = True
        events.draw_item_result = Result.success(ItemCode.SODA)

        result = game.perform_search_for_item()

        assert result is None
        assert events.draw_item_calls == 1
        assert items.find_item_calls == [ItemCode.SODA]
        assert state.find_item_calls == 1


    def test_search_for_item_advances_time_when_deck_shuffled(self, game):
        game, state, _, _, events = game

        state.is_searching_item = True
        events.draw_item_shuffled = True

        game.perform_search_for_item()

        assert state.advance_time_calls == 1


    def test_search_for_item_does_not_advance_time_without_shuffle(self, game):
        game, state, _, _, events = game

        state.is_searching_item = True
        events.draw_item_shuffled = False

        game.perform_search_for_item()

        assert state.advance_time_calls == 0


    # -----------------------------------------------------------------------------------------------------------
    # ignore_search_for_item
    # -----------------------------------------------------------------------------------------------------------


    def test_ignore_search_ends_search(self, game):
        game, state, _, _, _ = game

        state.is_searching_item = True

        result = game.ignore_search_for_item()

        assert result is None
        assert state.end_searching_item_calls == 1


    # -----------------------------------------------------------------------------------------------------------
    # take_item
    # -----------------------------------------------------------------------------------------------------------


    def test_take_item_keeps_found_item(self, game):
        game, state, _, items, _ = game

        state.has_found_item = True
        items.keep_found_item_result = None

        result = game.take_item()

        assert result is None
        assert items.keep_found_item_calls == 1
        assert state.end_found_item_calls == 1


    # -----------------------------------------------------------------------------------------------------------
    # dont_take_item
    # -----------------------------------------------------------------------------------------------------------

    def test_dont_take_item_when_no_item_found_returns_error(self, game):
        game, state, _, items, _ = game

        state.has_found_item = False

        result = game.dont_take_item()

        assert result == ErrorCode.HAVENT_FOUND_ITEM
        assert items.dont_take_item_calls == 0


    # -----------------------------------------------------------------------------------------------------------
    # discard_item
    # -----------------------------------------------------------------------------------------------------------

    def test_discard_item_delegates_to_items(self, game):
        game, _, _, items, _ = game

        items.discard_result = None

        result = game.discard_item(1)

        assert result is None
        assert items.discard_calls == [1]

    # -----------------------------------------------------------------------------------------------------------
    # use_item
    # -----------------------------------------------------------------------------------------------------------

    def test_use_soda_drinks_soda_after_successful_use(self, game):
        game, state, _, items, _ = game

        items.use_result = None

        result = game.use_item(ItemCode.SODA)

        assert result is None
        assert items.use_calls == [ItemCode.SODA]
        assert state.drink_soda_calls == 1


    # -----------------------------------------------------------------------------------------------------------
    # end_turn
    # -----------------------------------------------------------------------------------------------------------

    def test_end_turn_gets_tile_effect(self, game):
        game, state, movement, _, _ = game

        movement.tile_effect = "heal"

        result = game.end_turn()

        assert result is None
        assert movement.get_tile_effect_calls == 1
        assert state.do_end_turn_effect_calls == ["heal"]


    def test_end_turn_starts_new_turn_when_no_event_or_search(self, game):
        game, state, _, _, events = game

        state.is_doing_events = False
        state.is_searching_item = False

        result = game.end_turn()

        assert result is None
        assert state.start_new_turn_calls == 1
        assert events.draw_event_calls == []


    def test_end_turn_during_item_search_does_not_start_new_turn(self, game):
        game, state, _, _, _ = game

        state.is_doing_events = False
        state.is_searching_item = True

        result = game.end_turn()

        assert result is None
        assert state.start_new_turn_calls == 0


    def test_end_turn_during_events_draws_event(self, game):
        game, state, _, _, events = game

        state.is_doing_events = True

        result = game.end_turn()

        assert result is None
        assert events.draw_event_calls == [state.time]
        assert state.apply_card_effect_calls == ["event"]


    def test_cower_calls_state_cower_and_wastes_time(self, game):
        game, state, _, _, events = game

        result = game.end_turn(is_cower=True)

        assert result is None
        assert state.cower_calls == 1
        assert events.waste_time_calls == 1


    def test_cower_with_shuffled_card_advances_time(self, game):
        game, state, _, _, events = game

        events.waste_time_shuffled = True

        result = game.end_turn(is_cower=True)

        assert result is None
        assert state.advance_time_calls == 1


    def test_cower_without_shuffle_does_not_advance_time(self, game):
        game, state, _, _, events = game

        events.waste_time_shuffled = False

        result = game.end_turn(is_cower=True)

        assert result is None
        assert state.advance_time_calls == 0


    # -----------------------------------------------------------------------------------------------------------
    # check_win_loss
    # -----------------------------------------------------------------------------------------------------------

    def test_check_win_loss_returns_win(self, game):
        game, state, _, _, _ = game

        state.has_won = True
        state.has_lost = False

        result = game.check_win_loss()

        assert not result.is_fail()
        assert result.get_data() == "You win!"


    def test_check_win_loss_returns_loss(self, game):
        game, state, _, _, _ = game

        state.has_won = False
        state.has_lost = True

        result = game.check_win_loss()

        assert not result.is_fail()
        assert result.get_data() == "You lose!"


    def test_check_win_loss_returns_not_finished(self, game):
        game, state, _, _, _ = game

        state.has_won = False
        state.has_lost = False

        result = game.check_win_loss()

        assert result.is_fail()
        assert result.get_error_code() == ErrorCode.NOT_WON_OR_LOST
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

class TestGameBadDay:

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


    # -----------------------------------------------------------------------------------------------------------
    # move_player
    # -----------------------------------------------------------------------------------------------------------

    def test_move_player_when_movement_is_not_allowed_returns_error(self, game):
        game, state, movement, _, _ = game

        state.can_move = False

        result = game.move_player(Direction.NORTH)

        assert result == ErrorCode.CANT_MOVE_NOW
        assert movement.move_calls == []


    def test_move_player_propagates_movement_error(self, game):
        game, _, movement, _, _ = game

        movement.move_result = ErrorCode.INVALID_MOVE_NO_DOOR

        result = game.move_player(Direction.NORTH)

        assert result == ErrorCode.INVALID_MOVE_NO_DOOR


    # -----------------------------------------------------------------------------------------------------------
    # _draw_event_card / _do_post_event_checks
    # -----------------------------------------------------------------------------------------------------------

    def test_post_event_check_does_nothing_when_cannot_end_turn(self, game):
        game, state, movement, _, _ = game

        state.can_end_turn = False
        movement.needs_zombie_door = True
        state.has_ended_turn = True

        game.move_player(Direction.NORTH)

        assert movement.need_zombie_door_calls == 0
        assert state.start_zombie_door_calls == 0
        assert state.start_new_turn_calls == 0


    def test_post_event_check_does_not_start_new_turn_if_turn_not_ended(self, game):
        game, state, movement, _, _ = game

        state.can_end_turn = True
        movement.needs_zombie_door = False
        state.has_ended_turn = False

        game.move_player(Direction.NORTH)

        assert state.start_new_turn_calls == 0


    # -----------------------------------------------------------------------------------------------------------
    # rotate_tile
    # -----------------------------------------------------------------------------------------------------------

    def test_rotate_tile_when_not_moving_returns_error(self, game):
        game, state, movement, _, _ = game

        state.is_moving = False

        result = game.rotate_tile()

        assert result == ErrorCode.CANT_ROTATE_NOW
        assert movement.rotate_placement_tile_calls == 0


    def test_rotate_tile_propagates_movement_error(self, game):
        game, state, movement, _, _ = game

        state.is_moving = True
        movement.rotate_placement_tile_result = ErrorCode.CANT_MOVE_NOW

        result = game.rotate_tile()

        assert result == ErrorCode.CANT_MOVE_NOW


    # -----------------------------------------------------------------------------------------------------------
    # place_tile
    # -----------------------------------------------------------------------------------------------------------

    def test_place_tile_when_not_moving_returns_error(self, game):
        game, state, movement, _, _ = game

        state.is_moving = False

        result = game.place_tile()

        assert result == ErrorCode.CANT_PLACE_NOW
        assert movement.lock_placement_tile_calls == 0



    def test_place_tile_propagates_lock_error(self, game):
        game, state, movement, _, events = game

        state.is_moving = True
        movement.lock_placement_tile_result = ErrorCode.CANT_MOVE_NOW

        result = game.place_tile()

        assert result == ErrorCode.CANT_MOVE_NOW
        assert state.end_move_calls == 0
        assert events.draw_event_calls == []


    # -----------------------------------------------------------------------------------------------------------
    # pick_zombie_door
    # -----------------------------------------------------------------------------------------------------------

    def test_pick_zombie_door_when_not_in_mode_returns_error(self, game):
        game, state, movement, _, _ = game

        state.is_zombie_door = False

        result = game.pick_zombie_door(Direction.NORTH)

        assert result == ErrorCode.NOT_ZOMBIE_DOOR
        assert movement.create_zombie_door_calls == []


    def test_pick_zombie_door_propagates_movement_error(self, game):
        game, state, movement, _, _ = game

        state.is_zombie_door = True
        movement.create_zombie_door_result = ErrorCode.INVALID_MOVE_NO_DOOR

        result = game.pick_zombie_door(Direction.WEST)

        assert result == ErrorCode.INVALID_MOVE_NO_DOOR
        assert state.confirm_zombie_door_calls == 0


    # -----------------------------------------------------------------------------------------------------------
    # attack
    # -----------------------------------------------------------------------------------------------------------

    def test_attack_when_not_allowed_returns_error(self, game):
        game, state, movement, items, _ = game

        state.can_attack = False

        result = game.attack()

        assert result == ErrorCode.CANT_ATTACK
        assert items.attack_bonus_calls == []


    def test_attack_propagates_attack_bonus_error(self, game):
        game, state, _, items, _ = game

        items.attack_bonus_result = Result.fail(ErrorCode.NO_CHAINSAW)

        result = game.attack(use_chainsaw=True)

        assert result == ErrorCode.NO_CHAINSAW
        assert state.attack_calls == []
        assert items.record_battle_calls == 0


    def test_attack_with_instant_kill_requires_items(self, game):
        game, _, _, items, _ = game

        items.instant_kill_available = False

        result = game.attack(instant_kill=True)

        assert result == ErrorCode.NO_INSTANT_KILL
        assert items.discard_calls == []

    # -----------------------------------------------------------------------------------------------------------
    # flee
    # -----------------------------------------------------------------------------------------------------------

    def test_flee_when_not_allowed_returns_error(self, game):
        game, state, movement, _, _ = game

        state.can_flee = False

        result = game.flee(Direction.NORTH)

        assert result == ErrorCode.CANT_FLEE
        assert movement.flee_calls == []


    def test_flee_propagates_movement_error(self, game):
        game, state, movement, _, _ = game

        movement.flee_result = ErrorCode.INVALID_MOVE_NO_DOOR

        result = game.flee(Direction.NORTH)

        assert result == ErrorCode.INVALID_MOVE_NO_DOOR
        assert state.flee_calls == []


    def test_flee_with_oil_requires_oil(self, game):
        game, _, movement, items, _ = game

        items.has_oil = False

        result = game.flee(Direction.NORTH, with_oil=True)

        assert result == ErrorCode.NO_OIL
        assert movement.flee_calls == []


    # -----------------------------------------------------------------------------------------------------------
    # perform_search_for_item
    # -----------------------------------------------------------------------------------------------------------

    def test_search_for_item_when_not_searching_returns_error(self, game):
        game, state, _, _, events = game

        state.is_searching_item = False

        result = game.perform_search_for_item()

        assert result == ErrorCode.CANT_SEARCH_NOW
        assert events.draw_item_calls == 0


    def test_search_for_item_propagates_draw_error(self, game):
        game, state, _, items, events = game

        state.is_searching_item = True
        events.draw_item_result = Result.fail(ErrorCode.CANT_MOVE_NOW)

        result = game.perform_search_for_item()

        assert result == ErrorCode.CANT_MOVE_NOW
        assert items.find_item_calls == []
        assert state.find_item_calls == 0


    # -----------------------------------------------------------------------------------------------------------
    # ignore_search_for_item
    # -----------------------------------------------------------------------------------------------------------

    def test_ignore_search_when_not_searching_returns_error(self, game):
        game, state, _, _, _ = game

        state.is_searching_item = False

        result = game.ignore_search_for_item()

        assert result == ErrorCode.CANT_SEARCH_NOW
        assert state.end_searching_item_calls == 0


    # -----------------------------------------------------------------------------------------------------------
    # take_item
    # -----------------------------------------------------------------------------------------------------------

    def test_take_item_when_no_item_found_returns_error(self, game):
        game, state, _, items, _ = game

        state.has_found_item = False

        result = game.take_item()

        assert result == ErrorCode.HAVENT_FOUND_ITEM
        assert items.keep_found_item_calls == 0

    def test_take_item_propagates_inventory_error(self, game):
        game, state, _, items, _ = game

        state.has_found_item = True
        items.keep_found_item_result = ErrorCode.NO_SPACE

        result = game.take_item()

        assert result == ErrorCode.NO_SPACE
        assert state.end_found_item_calls == 0


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

    def test_discard_item_propagates_inventory_error(self, game):
        game, _, _, items, _ = game

        items.discard_result = ErrorCode.SLOT_EMPTY

        result = game.discard_item(0)

        assert result == ErrorCode.SLOT_EMPTY


    # -----------------------------------------------------------------------------------------------------------
    # use_item
    # -----------------------------------------------------------------------------------------------------------

    def test_use_item_propagates_inventory_error(self, game):
        game, state, _, items, _ = game

        items.use_result = ErrorCode.NO_SODA

        result = game.use_item(ItemCode.SODA)

        assert result == ErrorCode.NO_SODA
        assert state.drink_soda_calls == 0


    def test_use_non_soda_does_not_drink_soda(self, game):
        game, state, _, items, _ = game

        items.use_result = None

        result = game.use_item(ItemCode.OIL)

        assert result is None
        assert items.use_calls == [ItemCode.OIL]
        assert state.drink_soda_calls == 0


    # -----------------------------------------------------------------------------------------------------------
    # end_turn
    # -----------------------------------------------------------------------------------------------------------

    def test_end_turn_when_not_allowed_returns_error(self, game):
        game, state, movement, _, events = game

        state.can_end_turn = False

        result = game.end_turn()

        assert result == ErrorCode.CANT_END_TURN_NOW
        assert movement.get_tile_effect_calls == 0
        assert events.draw_event_calls == []


    def test_cower_failure_is_propagated(self, game):
        game, state, _, _, events = game

        state.cower_result = Result.fail(ErrorCode.CANT_END_TURN_NOW)

        result = game.end_turn(is_cower=True)

        assert result == ErrorCode.CANT_END_TURN_NOW
        assert events.waste_time_calls == 0


    def test_cower_waste_time_failure_is_propagated(self, game):
        game, state, _, _, events = game

        events.waste_time_result = Result.fail(ErrorCode.CANT_MOVE_NOW)

        result = game.end_turn(is_cower=True)

        assert result == ErrorCode.CANT_MOVE_NOW


    # -----------------------------------------------------------------------------------------------------------
    # check_win_loss
    # -----------------------------------------------------------------------------------------------------------

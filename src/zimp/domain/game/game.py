from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.result import Result

from zimp.domain.common.contract_items import ItemsContract
from zimp.domain.common.contract_movement import MovementContract
from zimp.domain.common.contract_events import EventsContract
from zimp.domain.common.contract_game_state import GameStateContract

from zimp.domain.common.item_code import ItemCode


class Game:
    """Boundary class connecting the controller to domain components"""

    def __init__(self,
                 state: GameStateContract,
                 movement: MovementContract,
                 items: ItemsContract,
                 events: EventsContract,
                 map_seed: int | None = None
                 ) -> None:
        self._state = state
        self._events = events
        self._items = items
        self._movement = movement

        self.reset(map_seed)

    def _draw_event_card(self) -> ErrorCode | None:
        draw_result, shuffled = self._events.draw_event(self._state.get_time())
        if draw_result.is_fail():
            return draw_result.get_error_code()

        print(draw_result.get_data())
        self._state.apply_card_effect(draw_result.get_data())
        if shuffled:
            self._state.advance_time()

        self._do_post_event_checks()

        return None

    def _do_post_event_checks(self) -> None:
        if self._state.get_can_end_turn():
            if self._movement.need_zombie_door():
                self._state.start_zombie_door()
            elif self._state.get_has_ended_turn():
                self._state.start_new_turn()

    def reset(self, map_seed: int | None = None) -> None:
        """Reset all game components"""
        self._state.reset()
        self._events.reset()
        self._movement.reset(randomizer_seed=map_seed) #408
        self._items.reset()

    def move_player(self, direction: Direction) -> ErrorCode | None:
        """Attempt to move the player in a given direction"""
        if not self._state.get_can_move():
            return ErrorCode.CANT_MOVE_NOW

        move_result = self._movement.move(direction)
        if isinstance(move_result, ErrorCode):
            return move_result

        if self._movement.is_placement_mode_on(): # Unknown tile
            self._state.start_move()
            return None

        return self._draw_event_card() # Known tile, skip placement

    def rotate_tile(self) -> ErrorCode | None:
        """Rotate the drawn tile in a given direction"""
        if not self._state.get_is_moving():
            return ErrorCode.CANT_ROTATE_NOW

        return self._movement.rotate_placement_tile()

    def place_tile(self) -> ErrorCode | None:
        """Attempt to place the drawn tile"""
        if not self._state.get_is_moving():
            return ErrorCode.CANT_PLACE_NOW

        place_result = self._movement.lock_placement_tile()
        if isinstance(place_result, ErrorCode):
            return place_result

        self._state.end_move()

        return self._draw_event_card()

    def pick_zombie_door(self, direction: Direction) -> ErrorCode | None:
        """Trigger a zombie door attack in the selected direction"""
        if not self._state.get_is_zombie_door():
            return ErrorCode.NOT_ZOMBIE_DOOR

        zombie_door_result = self._movement.create_zombie_door(direction)
        if isinstance(zombie_door_result, ErrorCode):
            return zombie_door_result

        self._state.confirm_zombie_door()

        return None

    def attack(self, use_chainsaw: bool = False, instant_kill:bool = False) -> ErrorCode | None:
        """Fight any zombies on the current tile"""
        if not self._state.get_can_attack():
            return ErrorCode.CANT_ATTACK

        if instant_kill:
            if not self._items.get_has_instant_kill():
                return ErrorCode.NO_INSTANT_KILL
            self._items.discard(0)
            self._items.discard(1)

        attack_bonus_result = self._items.attack_bonus(use_chainsaw)
        if attack_bonus_result.is_fail():
            return attack_bonus_result.get_error_code()

        attack_bonus = attack_bonus_result.get_data()
        self._state.attack(attack_bonus, instant_kill)

        self._items.record_battle()

        self._do_post_event_checks()

        return None

    def flee(self, direction: Direction, with_oil: bool = False) -> ErrorCode | None:
        """Flee to a previously explored tile"""
        if not self._state.get_can_flee():
            return ErrorCode.CANT_FLEE

        if with_oil and not self._items.get_has_oil():
            return ErrorCode.NO_OIL

        flee_move = self._movement.flee(direction)
        if isinstance(flee_move, ErrorCode):
            return flee_move

        self._state.flee(with_oil)

        if with_oil:
            self._items.use(ItemCode.OIL)

        self._do_post_event_checks()

        return None

    def perform_search_for_item(self) -> ErrorCode | None:
        """Draw a new card to find an item"""
        if not self._state.get_is_searching_item():
            return ErrorCode.CANT_SEARCH_NOW

        draw_result, shuffled = self._events.draw_item()
        if not draw_result.is_fail():
            self._items.find_item(draw_result.get_data())
            self._state.find_item()

            if shuffled:
                self._state.advance_time()

        return draw_result.get_error_code()

    def ignore_search_for_item(self) -> ErrorCode | None:
        """Choose not to draw a card to find an item"""
        if not self._state.get_is_searching_item():
            return ErrorCode.CANT_SEARCH_NOW

        self._state.end_searching_item()

        self._do_post_event_checks()

        return None

    def take_item(self) -> ErrorCode | None:
        """Add the found item to the items"""
        if not self._state.get_has_found_item():
            return ErrorCode.HAVENT_FOUND_ITEM

        add_item = self._items.keep_found_item()
        if isinstance(add_item, ErrorCode):
            return add_item

        self._state.end_found_item()

        self._do_post_event_checks()

        return None

    def dont_take_item(self) -> ErrorCode | None:
        """Abandon the item that was found"""
        if not self._state.get_has_found_item():
            return ErrorCode.HAVENT_FOUND_ITEM

        self._items.dont_take_item()
        self._state.end_found_item()

        self._do_post_event_checks()

        return None

    def discard_item(self, slot_id: int) -> ErrorCode | None:
        """Discard the chosen item from the items"""
        return self._items.discard(slot_id)

    def use_item(self, item_id: ItemCode) -> ErrorCode | None:
        """Use the chosen item (gasoline or soda)"""
        use = self._items.use(item_id)

        if isinstance(use, ErrorCode):
            return use

        if item_id == ItemCode.SODA:
            self._state.drink_soda()

        return None

    def end_turn(self, is_cower: bool = False) -> ErrorCode | None:
        """End the current turn, optionally cowering"""
        if not self._state.get_can_end_turn():
            return ErrorCode.CANT_END_TURN_NOW

        if is_cower:
            cower_action = self._state.cower()
            if cower_action.is_fail():
                return cower_action.get_error_code()

            cower_event, shuffled = self._events.waste_time()
            if cower_event.is_fail():
                return cower_event.get_error_code()
            if shuffled:
                self._state.advance_time()

        tile_effect = self._movement.get_tile_effect()
        print(tile_effect)
        self._state.do_end_turn_effect(tile_effect)

        if self._state.get_is_doing_events(): # temple or graveyard
            return self._draw_event_card()
        elif self._state.get_is_searching_item():
            pass
        else: #heal or none
            self._state.start_new_turn()

        return None

    def check_win_loss(self) -> Result:
        """To be called after each action; determines if the player has won or lost"""
        if self._state.check_is_won():
            return Result.success("You win!")
        elif self._state.check_is_lost():
            return Result.success("You lose!")

        return Result.fail(ErrorCode.NOT_WON_OR_LOST)

    def get_status(self) -> str:
        hp = self._state.get_hp()
        attack = 1+self._items.attack_bonus(False).get_data()
        items_tuple = self._items.held_items()
        items = f"{items_tuple[0]}, {items_tuple[1]}"
        return f"Health: {hp}, Attack: {attack}, Items: {items}"
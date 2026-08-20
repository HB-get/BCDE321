from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.item_code import ItemCode
from zimp.domain.game.game import Game
from zimp.domain.common.contract_game_state import GameStateContract
from zimp.domain.common.contract_movement import MovementContract
from zimp.domain.common.contract_items import ItemsContract
from zimp.domain.common.contract_events import EventsContract


class GameController:
    """Thin, testable boundary between Tkinter events and domain behaviour."""

    def __init__(
            self,
            state: GameStateContract,
            movement: MovementContract,
            items: ItemsContract,
            events: EventsContract,
    ) -> None:
        self._game = Game(state, movement, items, events)

    def reset(self) -> str:
        self._game.reset()
        return "Game reset."

    def move_up(self) -> str:
        result = self._game.move_player(Direction.NORTH)
        if result is None:
            return "Moved up."
        else:
            return str(result)

    def move_left(self) -> str:
        result = self._game.move_player(Direction.WEST)
        if result is None:
            return "Moved left."
        else:
            return str(result)

    def move_right(self) -> str:
        result = self._game.move_player(Direction.EAST)
        if result is None:
            return "Moved right."
        else:
            return str(result)

    def move_down(self) -> str:
        result = self._game.move_player(Direction.SOUTH)
        if result is None:
            return "Moved down."
        else:
            return str(result)

    def rotate_active_tile(self) -> str:
        result = self._game.rotate_tile()
        if result is None:
            return "Active tile rotated."
        else:
            return str(result)

    def place_active_tile(self) -> str:
        result = self._game.place_tile()
        if result is None:
            return "Active tile placed."
        else:
            return str(result)

    def zombie_door_up(self) -> str:
        result = self._game.pick_zombie_door(Direction.NORTH)
        if result is None:
            return "Zombie door from north."
        else:
            return str(result)

    def zombie_door_left(self) -> str:
        result = self._game.pick_zombie_door(Direction.WEST)
        if result is None:
            return "Zombie door from west"
        else:
            return str(result)

    def zombie_door_right(self) -> str:
        result = self._game.pick_zombie_door(Direction.EAST)
        if result is None:
            return "Zombie door from east"
        else:
            return str(result)


    def zombie_door_down(self) -> str:
        result = self._game.pick_zombie_door(Direction.SOUTH)
        if result is None:
            return "Zombie door from south"
        else:
            return str(result)

    def attack(self) -> str:
        result = self._game.attack()
        if result is None:
            return "Attacked."
        else:
            return str(result)

    def attack_with_chainsaw(self) -> str:
        result = self._game.attack(use_chainsaw=True)
        if result is None:
            return "Attacked with the chainsaw."
        else:
            return str(result)

    def attack_with_candle_fuel(self) -> str:
        result = self._game.attack(instant_kill=True)
        if result is None:
            return "Attacked with candle and fuel."
        else:
            return str(result)

    def flee_up(self) -> str:
        result = self._game.flee(Direction.NORTH)
        if result is None:
            return "Fled north."
        else:
            return str(result)

    def flee_left(self) -> str:
        result = self._game.flee(Direction.WEST)
        if result is None:
            return "Fled west."
        else:
            return str(result)

    def flee_right(self) -> str:
        result = self._game.flee(Direction.EAST)
        if result is None:
            return "Fled east."
        else:
            return str(result)

    def flee_down(self) -> str:
        result = self._game.flee(Direction.SOUTH)
        if result is None:
            return "Fled south."
        else:
            return str(result)

    def flee_up_with_oil(self) -> str:
        result = self._game.flee(Direction.NORTH, with_oil=True)
        if result is None:
            return "Fled north with oil."
        else:
            return str(result)

    def flee_left_with_oil(self) -> str:
        result = self._game.flee(Direction.WEST, with_oil=True)
        if result is None:
            return "Fled west with oil."
        else:
            return str(result)

    def flee_right_with_oil(self) -> str:
        result = self._game.flee(Direction.EAST, with_oil=True)
        if result is None:
            return "Fled east with oil."
        else:
            return str(result)

    def flee_down_with_oil(self) -> str:
        result = self._game.flee(Direction.SOUTH, with_oil=True)
        if result is None:
            return "Fled south with oil."
        else:
            return str(result)

    def end_turn(self) -> str:
        result = self._game.end_turn()
        if not isinstance(result, ErrorCode):
            return "Turn ended"
        else:
            return str(result)

    def cower_and_end_turn(self) -> str:
        result = self._game.end_turn(is_cower=True)
        if not isinstance(result, ErrorCode):
            return "Cowered and ended the turn."
        else:
            return str(result)

    def search_for_item(self) -> str:
        result = self._game.perform_search_for_item()
        if result is None:
            return "Searched for an item."
        else:
            return str(result)

    def dont_search_for_item(self) -> str:
        result = self._game.ignore_search_for_item()
        if result is None:
            return "Did not search for an item."
        else:
            return str(result)

    def take_found_item(self) -> str:
        result = self._game.take_item()
        if result is None:
            return "Took the found item."
        else:
            return str(result)

    def dont_take_found_item(self) -> str:
        result = self._game.dont_take_item()
        if result is None:
            return "Discarded the found item."
        else:
            return str(result)

    def discard_item_1(self) -> str:
        result = self._game.discard_item(0)
        if result is None:
            return "Discarded item 1."
        else:
            return str(result)

    def discard_item_2(self) -> str:
        result = self._game.discard_item(1)
        if result is None:
            return "Discarded item 2."
        else:
            return str(result)

    def use_soda(self) -> str:
        result = self._game.use_item(ItemCode.SODA)
        if result is None:
            return "Drank soda"
        else:
            return str(result)

    def use_gasoline(self) -> str:
        result = self._game.use_item(ItemCode.GASOLINE)
        if result is None:
            return "Refueled chainsaw."
        else:
            return str(result)

    def check_win_loss(self) -> str | None:
        result = self._game.check_win_loss()
        if not isinstance(result, ErrorCode):
            return result.get_data()
        else:
            return None

    def get_status(self) -> str:
        return self._game.get_status()
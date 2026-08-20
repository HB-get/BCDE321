import random

from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.result import Result
from zimp.domain.common.tile_effect import TileEffect
from zimp.domain.movement.tile import Tile
from zimp.domain.movement.validators import is_valid_seed


class TileManager:
    """TileManager class used to create and randomize map tiles."""

    # class constants
    __MIN_TILE_ID = 1
    __MAX_TILE_ID = 9
    __NUM_OF_TILES = 8
    __INSIDE_START_TILE_INDEX = 1
    __OUTSIDE_START_TILE_INDEX = 3

    def __init__(self):
        self.__inside_tile_order_index: int = 0
        self.__outside_tile_order_index: int = 0
        self.__inside_tile_order: list[int] = []
        self.__outside_tile_order: list[int] = []
        self.__INSIDE_TILE_DETAILS: dict[int, Tile] = {}
        self.__OUTSIDE_TILE_DETAILS: dict[int, Tile] = {}
        self.__tile_randomizer: random.Random = random.Random()  # class specific randomizer
        self.__randomizer_seed: int | None = None

        # setup tiles
        self.__create_tiles()
        self.reset_tile_order()

    def __create_tiles(self) -> None:
        """Creates inside and outside tile objects."""
        self.__INSIDE_TILE_DETAILS = {
            1: Tile(1, (Direction.NORTH,)),
            2: Tile(2, (Direction.NORTH, Direction.WEST)),
            3: Tile(3, (Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST), is_exit_tile=True),
            4: Tile(4, (Direction.NORTH, Direction.EAST, Direction.WEST)),
            5: Tile(5, (Direction.NORTH,)),
            6: Tile(6, (Direction.NORTH, Direction.EAST, Direction.WEST), TileEffect.HEALTH),
            7: Tile(7, (Direction.NORTH,), TileEffect.SEARCH),
            8: Tile(8, (Direction.EAST, Direction.WEST), TileEffect.FIND_TOTEM)
        }
        self.__OUTSIDE_TILE_DETAILS = {
            1: Tile(9, (Direction.EAST, Direction.SOUTH, Direction.WEST), is_outside_tile=True),
            2: Tile(10, (Direction.EAST, Direction.SOUTH, Direction.WEST), is_outside_tile=True),
            3: Tile(11, (Direction.NORTH, Direction.EAST, Direction.SOUTH), is_outside_tile=True, is_entry_tile=True),
            4: Tile(12, (Direction.SOUTH, Direction.WEST), is_outside_tile=True),
            5: Tile(13, (Direction.EAST, Direction.SOUTH, Direction.WEST), TileEffect.HEALTH, is_outside_tile=True),
            6: Tile(14, (Direction.EAST, Direction.SOUTH, Direction.WEST), is_outside_tile=True),
            7: Tile(15, (Direction.EAST, Direction.SOUTH, Direction.WEST), is_outside_tile=True),
            8: Tile(16, (Direction.EAST, Direction.SOUTH), TileEffect.BURY_TOTEM, is_outside_tile=True)
        }

    def __shuffle_tile_order(self) -> None:
        """Shuffles order of inside and outside tiles."""
        self.__tile_randomizer.seed(self.__randomizer_seed)
        inside_random_order = self.__tile_randomizer.sample(range(self.__MIN_TILE_ID, self.__MAX_TILE_ID),
                                                            k=self.__NUM_OF_TILES)
        outside_random_order = self.__tile_randomizer.sample(range(self.__MIN_TILE_ID, self.__MAX_TILE_ID),
                                                             k=self.__NUM_OF_TILES)

        # add inside/outside starting tiles to the start of each list
        inside_random_order.remove(self.__INSIDE_START_TILE_INDEX)
        outside_random_order.remove(self.__OUTSIDE_START_TILE_INDEX)
        inside_random_order.insert(0, self.__INSIDE_START_TILE_INDEX)
        outside_random_order.insert(0, self.__OUTSIDE_START_TILE_INDEX)

        self.__inside_tile_order = inside_random_order
        self.__outside_tile_order = outside_random_order

    def reset_tile_order(self, randomizer_seed: int | None = None) -> ErrorCode | None:
        """Resets the order of the inside and outside tiles.
        Args:
            randomizer_seed (int | None): New randomizer seed value. Defaults to None (random seed).
        Returns:
            ErrorCode: If seed was invalid. | None: If nothing went wrong.
        """
        if not is_valid_seed(randomizer_seed):
            return ErrorCode.INVALID_TYPE_RANDOMIZER_SEED

        self.__randomizer_seed = randomizer_seed
        self.__inside_tile_order_index = 0
        self.__outside_tile_order_index = 0
        self.__shuffle_tile_order()
        return None  # success

    def is_inside_tiles_depleted(self) -> bool:
        """Checks if player has explored all inside tiles.
        Returns:
            bool: True if player has explored all inside tiles, False otherwise.
        """
        return self.__inside_tile_order_index >= len(self.__inside_tile_order)

    def is_outside_tiles_depleted(self) -> bool:
        """Checks if player has explored all outside tiles.
        Returns:
            bool: True if player has explored all outside tiles, False otherwise.
        """
        return self.__outside_tile_order_index >= len(self.__outside_tile_order)

    def get_next_inside_tile(self) -> Result:
        """Gets the next inside tile following the randomized order.
        Returns:
            Result: Success - next inside tile. | Fail - ErrorCode.
        """
        if self.is_inside_tiles_depleted():
            return Result.fail(ErrorCode.DEPLETED_INSIDE_TILES)

        # gets next tile
        index = self.__inside_tile_order[self.__inside_tile_order_index]
        new_tile = self.__INSIDE_TILE_DETAILS.get(index)
        if new_tile is None:
            return Result.fail(ErrorCode.FATAL_ERROR)

        # increments index and returns tile
        self.__inside_tile_order_index += 1
        return Result.success(new_tile)

    def get_next_outside_tile(self) -> Result:
        """Gets the next outside tile following the randomized order.
        Returns:
            Result: Success - next outside tile. | Fail - ErrorCode.
        """
        if self.is_outside_tiles_depleted():
            return Result.fail(ErrorCode.DEPLETED_OUTSIDE_TILES)

        # gets next tile
        index = self.__outside_tile_order[self.__outside_tile_order_index]
        new_tile = self.__OUTSIDE_TILE_DETAILS.get(index)
        if new_tile is None:
            return Result.fail(ErrorCode.FATAL_ERROR)

        # increments index and returns tile
        self.__outside_tile_order_index += 1
        return Result.success(new_tile)

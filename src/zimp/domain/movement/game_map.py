from typing import Final

from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.result import Result
from zimp.domain.common.tile_data import TileData
from zimp.domain.common.tile_effect import TileEffect
from zimp.domain.movement.tile import Tile
from zimp.domain.movement.tile_manager import TileManager
from zimp.domain.movement.validators import is_valid_point_type, is_valid_point_within_range, validate_map_and_position, \
    is_move_valid, is_valid_direction


class GameMap:
    """GameMap class used to hold and calculate tile placement and player movement data.
    Args:
        map_dimensions (tuple[int, int]): Map dimensions (width, height) (1-indexed). Defaults to (5, 5).
        starting_position (tuple[int, int]): Starting position (X, Y) (0-indexed). Defaults to (2, 4).
        randomizer_seed (int): Seed used to randomly order tiles. Defaults to None (random seed).
    """

    # class constants
    __DEFAULT_MAP_DIMENSIONS: Final[tuple[int, int]] = (5, 5)
    __DEFAULT_START_POSITION: Final[tuple[int, int]] = (2, 4)
    __DEFAULT_MINIMUM_MAP_DIMENSIONS: Final[tuple[int, int]] = (4, 4)
    __DEFAULT_MINIMUM_START_POSITION: Final[tuple[int, int]] = (0, 0)

    def __init__(self, map_dimensions: tuple[int, int] = __DEFAULT_MAP_DIMENSIONS,
                 starting_position: tuple[int, int] = __DEFAULT_START_POSITION,
                 randomizer_seed: int | None = None) -> None:
        # map dimension type check
        if not is_valid_point_type(map_dimensions):
            raise TypeError("Invalid map dimensions type, must be a tuple of two integers")
        # map dimension value check
        if not is_valid_point_within_range(map_dimensions, self.__DEFAULT_MINIMUM_MAP_DIMENSIONS):
            raise ValueError(
                f"Map dimensions must be greater than {self.__DEFAULT_MINIMUM_MAP_DIMENSIONS[0]}x{self.__DEFAULT_MINIMUM_MAP_DIMENSIONS[1]}")

        # starting position type check
        if not is_valid_point_type(starting_position):
            raise TypeError("Invalid starting position type, must be a tuple of two integers")
        # starting position value check
        if not is_valid_point_within_range(starting_position, self.__DEFAULT_MINIMUM_START_POSITION, map_dimensions):
            raise ValueError("Starting position must be within the map dimensions")

        # add tile manager
        self.__tile_manager = TileManager()

        # seed value check
        if self.__tile_manager.reset_tile_order(randomizer_seed) is not None:
            raise TypeError("Randomizer seed must be an integer")

        # map details
        self.__map_dimensions: tuple[int, int] = map_dimensions
        self.__starting_position: tuple[int, int] = starting_position
        self.__display_tiles: dict[tuple[int, int], Tile] = {}
        self.__player_position: tuple[int, int] = self.__starting_position
        # tile placement details
        self.__is_placement_mode_on: bool = False
        self.__player_is_outside: bool = False
        self.__last_added_tile: Tile
        self.__last_move_direction: Direction
        self.__last_move_destination_position: tuple[int, int]

        # setup map
        self.__setup()

    def __setup(self) -> None:
        """Sets up the game map."""
        self.__player_is_outside = False
        self.__is_placement_mode_on = False
        self.__player_position = self.__starting_position

        self.__add_tile(self.__starting_position)  # add start tile
        self.__display_tiles[self.__starting_position].lock()  # lock first tile

    def __add_tile(self, position: tuple[int, int]) -> ErrorCode | None:
        """Adds next tile to the displayed tiles.
        Args:
            position (tuple[int, int]): Position to add.
        Returns:
            ErrorCode: If something went wrong. | None: If nothing went wrong.
        """
        if self.__player_is_outside:
            tile_result = self.__tile_manager.get_next_outside_tile()
        else:
            tile_result = self.__tile_manager.get_next_inside_tile()

        if tile_result.is_fail():
            return tile_result.get_error_code()

        # add tile using position as key
        self.__display_tiles[position] = tile_result.get_data()
        self.__last_added_tile = tile_result.get_data()
        return None  # success

    def __update_player_area(self, move_direction: Direction, current_tile: Tile) -> None:
        """Updates player area if transitioning between inside/outside areas through the entry/exit doors.
        Args:
            move_direction (Direction): Direction player is moving towards.
            current_tile (Tile): The tile the player is currently on.
        """
        # checks if moving through transition door (north door when not rotated)
        moving_through_transition_door = move_direction == current_tile.get_rotation()
        if current_tile.is_exit() and moving_through_transition_door:
            self.__player_is_outside = True
        elif current_tile.is_entry() and moving_through_transition_door:
            self.__player_is_outside = False

    def __is_exit_clear(self, new_tile_direction: Direction) -> bool:
        """Checks if the exit tiles transition door (NORTH) points to an empty tile.
        Args:
            new_tile_direction (Direction): Direction the tile is rotated.
        Returns:
            bool: True if not the exit tile or the transition door points to an empty tile, False otherwise.
        """
        if not self.__last_added_tile.is_exit():
            return True  # if the tile is not an exit tile no need to check

        # get the position the exit tile arrow is pointing at
        next_tile_pos_result = self.__calculate_position(self.__last_move_destination_position, new_tile_direction)
        if next_tile_pos_result.is_fail():
            return False  # cant point to invalid position

        if self.__display_tiles.get(next_tile_pos_result.get_data()) is not None:
            return False  # exit arrow cant point to existing tile

        return True  # exit arrow pointing at blank tile

    def __is_entry_aligned(self, new_tile_direction: Direction) -> bool:
        """Checks if the entry tiles transition door (NORTH) points at the exit tile.
        Args:
            new_tile_direction (Direction): Direction the tile is rotated.
        Returns:
            bool: True if not the entry tile or the transition door points at the exit tile, False otherwise.
        """
        if not self.__last_added_tile.is_entry():
            return True  # if the tile is not an entry tile no need to check

        # get the position the entry tile arrow is pointing at
        next_tile_pos_result = self.__calculate_position(self.__last_move_destination_position, new_tile_direction)
        if next_tile_pos_result.is_fail():
            return False  # cant point to invalid position

        past_tile = self.__display_tiles.get(next_tile_pos_result.get_data())
        if past_tile is None or not past_tile.is_exit():
            return False  # entry arrow cant point to blank tile or tile that is NOT the exit

        return True  # entry arrow pointing at exit tile

    def __calculate_placement_tile_rotation(self) -> ErrorCode | None:
        """Rotates new tile until doors are aligned.
        Returns:
            ErrorCode: If something went wrong. | None: If nothing went wrong.
        """
        original_rotation = self.__last_added_tile.get_rotation()

        # loop through each direction and rotates tile
        for i in range(4):
            new_tile_direction = Direction((original_rotation.value + (90 * i)) % 360)
            self.__last_added_tile.rotate(new_tile_direction)

            # check if doors align
            if self.__last_added_tile.has_door_in_opposite_direction(self.__last_move_direction):
                if not self.__is_exit_clear(new_tile_direction):
                    continue  # if exit is not clear then invalid rotation, skip to next rotation
                if not self.__is_entry_aligned(new_tile_direction):
                    continue  # if entry is not aligned then invalid rotation, skip to next rotation

                return None  # valid rotation found

        # if no rotation is valid the tile cant be placed
        return ErrorCode.FATAL_UNPLACEABLE_TILE

    def __setup_placement_tile(self, move_direction: Direction, current_tile: Tile,
                               destination_position: tuple[int, int]) -> ErrorCode | None:
        """Adds next tile and sets its rotation.
        Args:
            move_direction (Direction): Direction player is moving towards.
            current_tile (Tile): The tile the player is currently on.
            destination_position (tuple[int, int]): Position the player is moving towards.
        Returns:
            ErrorCode: If something went wrong. | None: If nothing went wrong.
        """
        # check if player is transitioning between areas and add tile
        self.__update_player_area(move_direction, current_tile)
        add_error = self.__add_tile(destination_position)
        if add_error is not None:
            return add_error

        # save direction and position
        self.__last_move_direction = move_direction
        self.__last_move_destination_position = destination_position

        # find tile rotation and return any error
        place_error = self.__calculate_placement_tile_rotation()
        if place_error is not None:
            return place_error

        return None  # success

    def __calculate_position(self, position: tuple[int, int], direction: Direction) -> Result:
        """Calculates the new position from the given position and direction.
        Args:
            position (tuple[int, int]): Current position.
            direction (Direction): Direction from the current position to the new position.
        Returns:
            Result: Success - new position. | Fail - ErrorCode.
        """
        # calculate new position
        new_pos: tuple[int, int]
        match direction:
            case Direction.NORTH:
                new_pos = (position[0], position[1] - 1)
            case Direction.SOUTH:
                new_pos = (position[0], position[1] + 1)
            case Direction.WEST:
                new_pos = (position[0] - 1, position[1])
            case Direction.EAST:
                new_pos = (position[0] + 1, position[1])

        # validates new position
        if not is_valid_point_within_range(new_pos, self.__DEFAULT_MINIMUM_START_POSITION, self.__map_dimensions):
            return Result.fail(ErrorCode.INVALID_MOVE_OUT_OF_BOUNDS)

        return Result.success(new_pos)  # success

    def __handle_move_to_blank_tile(self, direction: Direction, current_tile: Tile,
                                    destination_position: tuple[int, int]) -> ErrorCode | None:
        """Checks move to blank tile and setups placement tile.
        Args:
            direction (Direction): Direction player is trying to move.
            current_tile (Tile): Current tile the player is on.
            destination_position (tuple[int, int]): Position the player is trying to move to.
        Returns:
            ErrorCode: If something went wrong. | None: If nothing went wrong.
        """
        if not current_tile.has_door_in_direction(direction):
            return ErrorCode.INVALID_MOVE_NO_DOOR  # no door opens in given direction

        # setup placement and return any error
        setup_place_error = self.__setup_placement_tile(direction, current_tile, destination_position)
        if setup_place_error is not None:
            return setup_place_error

        return None  # success

    def __handle_move_to_known_tile(self, direction: Direction, destination_tile: Tile, current_tile: Tile,
                                    destination_position: tuple[int, int]) -> ErrorCode | None:
        """Checks move to known tile and moves player to destination tile.
        Args:
            direction (Direction): Direction player is trying to move.
            destination_tile (Tile): Destination tile the player is trying to move to.
            current_tile (Tile): Current tile the player is on.
            destination_position (tuple[int, int]): Position the player is trying to move to.
        Returns:
            ErrorCode: If something went wrong. | None: If nothing went wrong.
        """
        move_error = is_move_valid(current_tile, destination_tile, direction)
        if move_error is not None:
            return move_error  # invalid move

        # valid move updates player
        self.__update_player_area(direction, current_tile)
        self.__player_position = destination_position
        return None  # success

    def __move_player(self, direction: Direction, is_flee: bool) -> ErrorCode | None:
        """Attempts to move the player in the given direction.

         The method does different actions depending on the mode:
         MOVE (NOT FLEE):
             Turns ON tile placement if move is valid and destination is empty.
             Moves player if destination is known and move is valid.
         FLEE:
             Moves player if destination is known and move is valid.

         Args:
             direction (Direction): Direction the player wants to move.
             is_flee (bool): If the player is fleeing or not.
         Returns:
               ErrorCode: If something went wrong. | None: If nothing went wrong.
         """
        if self.__is_placement_mode_on:
            return ErrorCode.INVALID_ACTION_PLACEMENT_MODE_ON  # prevents moves while placement mode is on

        if not is_valid_direction(direction):
            return ErrorCode.INVALID_VALUE_DIRECTION

        # get tile player is currently on
        current_tile = self.__display_tiles.get(self.__player_position)
        if current_tile is None:
            return ErrorCode.FATAL_ERROR  # tile player is on is missing

        # get new position
        destination_position_result = self.__calculate_position(self.__player_position, direction)
        if destination_position_result.is_fail():
            return destination_position_result.get_error_code()  # error when trying to get position

        # get dest position and tile
        destination_position = destination_position_result.get_data()
        destination_tile = self.__display_tiles.get(destination_position)

        if destination_tile is None:
            if is_flee:
                return ErrorCode.INVALID_MOVE_FLEE_TO_UNKNOWN_TILE  # cant flee to unknown tile

            # move to blank tile, return any error
            error = self.__handle_move_to_blank_tile(direction, current_tile, destination_position)
            if error is not None:
                return error

            self.__is_placement_mode_on = True  # placement mode ON
            return None

        else:
            # move to known tile, return any error
            return self.__handle_move_to_known_tile(direction, destination_tile, current_tile,
                                                    destination_position)

    def move(self, direction: Direction) -> ErrorCode | None:
        """Attempts to move the player in the given direction.
        Args:
            direction (Direction): Direction player is trying to move.
        Returns:
            ErrorCode: If something went wrong. | None: If nothing went wrong.
        """
        return self.__move_player(direction, False)

    def flee(self, direction: Direction) -> ErrorCode | None:
        """Attempts to flee the player in the given direction.
        Args:
            direction (Direction): Direction player is trying to move.
        Returns:
            ErrorCode: If something went wrong. | None: If nothing went wrong.
        """
        return self.__move_player(direction, True)

    def create_zombie_door(self, direction: Direction) -> ErrorCode | None:
        """Attempts to create a zombie door in the given direction.

         If the destination is empty and valid a zombie door is created on the current
         tile in the given direction.

         Args:
             direction (Direction): Direction the player wants to move.
         Returns:
               ErrorCode: If something went wrong. | None: If nothing went wrong.
         """
        if self.__is_placement_mode_on:
            return ErrorCode.INVALID_ACTION_PLACEMENT_MODE_ON  # prevents moves while placement mode is on

        if not is_valid_direction(direction):
            return ErrorCode.INVALID_VALUE_DIRECTION

        # get new position
        destination_position_result = self.__calculate_position(self.__player_position, direction)
        if destination_position_result.is_fail():
            return destination_position_result.get_error_code()  # error when trying to get position

        # get dest position and tile
        destination_position = destination_position_result.get_data()
        destination_tile = self.__display_tiles.get(destination_position)

        if destination_tile is not None:
            return ErrorCode.INVALID_MOVE_ZOMBIE_DOOR_TO_KNOWN_TILE  # cant make door to known tile

        # add zombie door
        self.__last_added_tile.add_zombie_door(direction)
        return None  # success

    def rotate_placement_tile(self) -> ErrorCode | None:
        """Rotates the currently placeable tile.
        Returns:
            ErrorCode: If the tile is locked. | None: If nothing went wrong.
        """
        # cannot rotate if locked
        if self.__last_added_tile.is_locked():
            return ErrorCode.INVALID_ACTION_ROTATE_LOCKED_TILE

        # rotate tile and calculate next valid rotation
        self.__last_added_tile.rotate(Direction((self.__last_added_tile.get_rotation().value + 90) % 360))
        self.__calculate_placement_tile_rotation()
        return None  # success

    def lock_placement_tile(self) -> ErrorCode | None:
        """Locks the placement of the currently placeable tile and move the player to it.
        Returns:
            ErrorCode: If the tile is locked. | None: If nothing went wrong.
        """
        # cannot rotate if locked
        if self.__last_added_tile.is_locked():
            return ErrorCode.INVALID_ACTION_LOCK_LOCKED_TILE

        # lock tile placement and move player
        self.__last_added_tile.lock()
        self.__player_position = self.__last_move_destination_position
        self.__is_placement_mode_on = False  # turn placement mode OFF
        return None  # success

    def need_zombie_door(self) -> bool:
        """Checks if a zombie door is needed.

        Zombie doors are needed if the player is inside/outside, no normal doors open to an
        empty tile, and not all tiles have been explored.

        Returns:
            bool: True if a zombie door is needed, False otherwise.
        """
        # check if all inside/outside tiles have been explored
        if self.__player_is_outside and self.__tile_manager.is_outside_tiles_depleted():
            return False
        if not self.__player_is_outside and self.__tile_manager.is_inside_tiles_depleted():
            return False

        # loop through all displayed tiles
        for position, tile in self.__display_tiles.items():
            if self.__player_is_outside != tile.is_outside():
                continue  # skip if player does not match tile area

            # check if doors open to blank tiles
            for door_direction in tile.get_door_directions():
                pos_result = self.__calculate_position(position, door_direction)
                if pos_result.is_fail():
                    continue  # skip if door opens to position that is out of bounds

                # check where door opens to
                if self.__display_tiles.get(pos_result.get_data()) is None:
                    if tile.is_exit() and door_direction == tile.get_rotation():
                        continue  # skip if exit tile and transition door opens to blank tile

                    return False  # if any door opens to a blank tile then no need for zombie door
        return True  # if NO doors open to blank tiles then a zombie door is needed

    def is_placement_mode_on(self) -> bool:
        """Checks if the placement mode is on.
        Returns:
            bool: True if the placement mode is on, False otherwise.
        """
        return self.__is_placement_mode_on

    def get_tile_data(self) -> list[TileData]:
        """Gets the data for all the tiles being displayed.
        Returns:
            list[TileData]: The tile data.
        """
        data = []
        for position, tile in self.__display_tiles.items():
            data.append(tile.get_data(position))
        return data

    def get_player_position(self) -> tuple[int, int]:
        """Gets the players current position.
        Returns:
            tuple[int, int]: The players position.
        """
        return self.__player_position

    def get_tile_effect(self) -> TileEffect:
        """Gets the tile effect of the tile the player is currently on.
        Returns:
            TileEffect: The tile effect of the tile. | None: If there is no tile effect.
        """
        return self.__display_tiles[self.__player_position].get_tile_effect()

    def get_map_dimensions(self) -> tuple[int, int]:
        """Gets the map dimensions of the game map.
        Returns:
            tuple[int, int]: The map dimensions.
        """
        return self.__map_dimensions

    def reset(self, map_dimensions: tuple[int, int] | None = None, starting_position: tuple[int, int] | None = None,
              randomizer_seed: int | None = None) -> ErrorCode | None:
        """Resets the game map to its initial state.
        Args:
            map_dimensions (tuple[int, int] | None): New map dimensions (width, height) (1-indexed).
                Defaults to None (uses previous map dimensions).
            starting_position (tuple[int, int] | None): New starting position (X, Y) (0-indexed).
                Defaults to None (uses previous starting position).
            randomizer_seed (int | None): New randomizer seed. Defaults to None (random seed).
        Returns:
            ErrorCode: If something went wrong. | None: If nothing went wrong.
        """
        # checks map dimensions and start position
        map_start_validation_error = validate_map_and_position(self.__map_dimensions, self.__player_position,
                                                               self.__DEFAULT_MINIMUM_MAP_DIMENSIONS,
                                                               self.__DEFAULT_MINIMUM_START_POSITION,
                                                               map_dimensions, starting_position)
        if map_start_validation_error is not None:
            return map_start_validation_error

        # checks seed
        seed_error = self.__tile_manager.reset_tile_order(randomizer_seed)
        if seed_error is not None:
            return seed_error

        # assigns new map and start
        if map_dimensions is not None:
            self.__map_dimensions = map_dimensions
        if starting_position is not None:
            self.__starting_position = starting_position

        # reset map and clears all displayed tiles
        for position, tile in self.__display_tiles.items():
            tile.reset()
        self.__display_tiles.clear()
        self.__setup()
        return None  # success

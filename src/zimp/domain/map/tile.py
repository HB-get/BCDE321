from zimp.domain.common.direction import Direction
from zimp.domain.common.tile_data import TileData
from zimp.domain.common.tile_effect import TileEffect


class Tile:
    """Tile class used to hold and calculate data for an individual tile.
    Args:
        tile_id (int): ID of the tile.
        doors (list[Door]): List of doors.
        tile_effect (TileEffect): Effect of the tile. Defaults to None.
        is_outside_tile (bool): Whether the tile is outside. Defaults to False.
        is_exit_tile (bool): Whether the tile is the inside exit tile. Defaults to False.
        is_entry_tile (bool): Whether the tile is the outside entry tile. Defaults to False.
    """

    def __init__(self, tile_id: int, doors: tuple[Direction, ...], tile_effect: TileEffect = TileEffect.NONE,
                 is_outside_tile: bool = False, is_exit_tile: bool = False, is_entry_tile: bool = False) -> None:
        self.__id = tile_id
        self.__doors = doors
        self.__tile_effect = tile_effect
        self.__is_outside_tile = is_outside_tile
        self.__is_exit_tile = is_exit_tile
        self.__is_entry_tile = is_entry_tile
        self.__zombie_door = None
        self.__rotation = Direction.NORTH
        self.__is_locked = False

    def get_tile_effect(self) -> TileEffect:
        return self.__tile_effect

    def get_rotation(self) -> Direction:
        return self.__rotation

    def is_outside(self) -> bool:
        return self.__is_outside_tile

    def is_exit(self) -> bool:
        return self.__is_exit_tile

    def is_entry(self) -> bool:
        return self.__is_entry_tile

    def is_locked(self) -> bool:
        return self.__is_locked

    def lock(self) -> None:
        self.__is_locked = True

    def rotate(self, direction: Direction) -> None:
        self.__rotation = direction

    def get_door_directions(self) -> tuple[Direction, ...]:
        """Gets the direction the tiles doors open towards.
        Returns:
            tuple[Direction]: List of directions of the tiles doors.
        """
        # adds the rotation to get the correct direction
        door_directions = tuple(
            map(lambda direction: Direction((direction.value + self.__rotation.value) % 360), self.__doors))

        # adds zombie door direction if not none
        if self.__zombie_door is None:
            return door_directions
        else:
            return *door_directions, self.__zombie_door

    def has_door_in_direction(self, direction: Direction) -> bool:
        """Checks if the tile has a door in the given direction.
        Args:
            direction (Direction): Direction to check.
        Returns:
            bool: True if the tile has a door in the direction, False if not.
        """
        door_directions = self.get_door_directions()
        for d in door_directions:
            if d == direction:
                return True
        return False

    def has_door_in_opposite_direction(self, direction: Direction) -> bool:
        """Checks if the tile has a door in the opposite given direction.
        Args:
            direction (Direction): Direction to check.
        Returns:
            bool: True if the tile has a door in the opposite direction, False if not.
        """
        # calculates opposite direction
        opposite_rotation = 180
        opposite_direction = Direction((direction.value + opposite_rotation) % 360)

        return self.has_door_in_direction(opposite_direction)

    def add_zombie_door(self, direction: Direction) -> None:
        """Adds a zombie door to the tile in the given direction.
        Args:
            direction (Direction): Direction of the zombie door.
        """
        self.__zombie_door = direction

    def reset(self) -> None:
        """Resets the tiles mutable data to its default values."""
        self.__zombie_door = None
        self.__rotation = Direction.NORTH
        self.__is_locked = False

    def get_data(self, position: tuple[int, int]) -> TileData:
        """Gets the tiles id, position, rotation, zombie door and locked value.
        Args:
            position (tuple[int, int]): Position of the tile.
        Returns:
            TileData: Object containing the tiles data.
        """
        return TileData(self.__id, position, self.__rotation, self.__zombie_door, self.__is_locked)

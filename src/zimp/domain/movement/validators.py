from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.movement.tile import Tile


def is_valid_direction(value: Direction) -> bool:
    """Checks if the given value is a valid direction.
    Args:
        value (Direction): Value to be checked.
    Returns:
        bool: True if the given value is a valid direction, False otherwise.
    """
    return isinstance(value, Direction)


def is_valid_point_type(value: tuple[int, int]) -> bool:
    """Checks if the given value is a valid tuple of (int, int).
    Args:
        value (tuple[int, int]): Value to be checked.
    Returns:
        bool: True if the given value is a valid tuple of (int, int), False otherwise.
    """
    return (isinstance(value, tuple) and len(value) == 2
            and isinstance(value[0], int) and isinstance(value[1], int))


def is_point_lesser(first_value: tuple[int, int], second_value: tuple[int, int]) -> bool:
    """Checks if either int in the first value is less than either int in the second value.
    Args:
        first_value (tuple[int, int]): First value containing two integers.
        second_value (tuple[int, int]): Second value containing two integers.
    Returns:
        bool: True if either int in the first value is less than either int in the second value, False otherwise.
    """
    return first_value[0] < second_value[0] or first_value[1] < second_value[1]


def is_point_greater_or_equal(first_value: tuple[int, int], second_value: tuple[int, int]) -> bool:
    """Checks if either int in the first value is greater or equal than either int in the second value.
    Args:
        first_value (tuple[int, int]): First value containing two integers.
        second_value (tuple[int, int]): Second value containing two integers.
    Returns:
        bool: True if either int in the first value is greater or equal than either int in the second value, False otherwise.
    """
    return first_value[0] >= second_value[0] or first_value[1] >= second_value[1]


def is_valid_seed(value: int | None) -> bool:
    """Checks if the given value is a valid seed type.
    Args:
        value (int | None): Seed value to check.
    Returns:
        bool: True if the given value is an int or None, False otherwise.
    """
    return value is None or isinstance(value, int)


def is_valid_point_within_range(value: tuple[int, int], lower_limit: tuple[int, int],
                                upper_limit: tuple[int, int] | None = None) -> bool:
    """Checks if value is within the range of the given lower and upper limit.

    If either int in the value is less than the lower limit the value is not within range.
    If either int in the value is greater or equal to the upper limit the value is not within range.
    If the upper limit is not given then it is not checked.

    Args:
        value (tuple[int, int]): Value containing two integers.
        lower_limit (tuple[int, int]): Value containing two integers.
        upper_limit (tuple[int, int] | None): Value containing two integers. Defaults to None.
    Returns:
        bool: True if value is within the range of the given lower and upper limit, False otherwise.
    """
    if is_point_lesser(value, lower_limit):
        return False

    if upper_limit is not None and is_point_greater_or_equal(value, upper_limit):
        return False

    return True


def validate_map_and_position(old_map_dim: tuple[int, int], old_start_pos: tuple[int, int],
                              min_map_dim: tuple[int, int], min_start_pos: tuple[int, int],
                              new_map_dim: tuple[int, int] | None = None,
                              new_start_pos: tuple[int, int] | None = None) -> ErrorCode | None:
    """Validates the map dimensions and starting position.

    Checks that the new map dimension and starting position is valid and the starting position is within
    the new map size. If a new starting position is not given then the existing starting position is used.
    If a new map dimension is not given then the existing map dimension is used.

    Args:
        old_map_dim (tuple[int, int]): Old map dimensions.
        old_start_pos (tuple[int, int]): Old start position.
        min_map_dim (tuple[int, int]): Minimum map dimensions.
        min_start_pos (tuple[int, int]): Minimum start position.
        new_map_dim (tuple[int, int]): New map dimensions.
        new_start_pos (tuple[int, int]): New start position.
    Returns:
        ErrorCode: If something went wrong. | None: If nothing went wrong.
    """
    # check map dimension type
    if new_map_dim is not None and not is_valid_point_type(new_map_dim):
        return ErrorCode.INVALID_TYPE_MAP_DIMENSION

    # check start position type
    if new_start_pos is not None and not is_valid_point_type(new_start_pos):
        return ErrorCode.INVALID_TYPE_STARTING_POSITION

    if new_map_dim is not None and new_start_pos is None:
        # check map dimensions still work with current start position
        if is_point_greater_or_equal(old_start_pos, new_map_dim) or is_point_lesser(new_map_dim, min_map_dim):
            return ErrorCode.INVALID_VALUE_MAP_DIMENSION
    elif new_map_dim is None and new_start_pos is not None:
        # check starting position fits with current map dimensions
        if not is_valid_point_within_range(new_start_pos, min_start_pos, old_map_dim):
            return ErrorCode.INVALID_VALUE_STARTING_POSITION
    elif new_map_dim is not None and new_start_pos is not None:
        # check new start position fits in new map dimensions
        if (not is_valid_point_within_range(new_start_pos, min_start_pos, new_map_dim)
                or is_point_lesser(new_map_dim, min_map_dim)):
            return ErrorCode.INVALID_VALUE_STARTING_POSITION

    return None  # success


def is_move_valid(current_tile: Tile, destination_tile: Tile, direction: Direction) -> ErrorCode | None:
    """Checks both tiles have aligned doors, the move is through the transition doors or both tiles are inside/outside.
    Args:
        current_tile (Tile): Current tile the player is on.
        destination_tile (Tile): Destination tile the player is trying to move to.
        direction (Direction): Direction from the current tile to the destination tile.
    Returns:
        ErrorCode: If something went wrong. | None: If nothing went wrong.
    """
    doors_align = (current_tile.has_door_in_direction(direction)
                   and destination_tile.has_door_in_opposite_direction(direction))
    is_move_between_connection = ((current_tile.is_exit() and destination_tile.is_entry())
                                  or (destination_tile.is_exit() and current_tile.is_entry()))
    is_same_area = current_tile.is_outside() == destination_tile.is_outside()

    if not doors_align:
        return ErrorCode.INVALID_MOVE_NO_DOOR
    elif not (is_move_between_connection or is_same_area):
        return ErrorCode.INVALID_MOVE_ACROSS_AREAS

    return None  # success

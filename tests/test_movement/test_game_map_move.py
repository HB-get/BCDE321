import pytest

from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.direction import Direction
from zimp.domain.movement.game_map import GameMap


# ========================== Good Day ========================== #


def test_move_when_given_valid_direction_to_empty_tile_returns_none_and_turns_on_placement_mode() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2))
    move_direction = Direction.NORTH

    # Act
    move_error = movement.move(move_direction)
    mode_value = movement.is_placement_mode_on()

    # Assert
    assert move_error is None
    assert mode_value is True


def test_move_when_given_valid_direction_to_empty_tile_does_not_move_player_to_tile() -> None:
    # Arrange
    starting_position = (2, 2)
    movement = GameMap(map_dimensions=(5, 5), starting_position=starting_position)
    move_direction = Direction.NORTH

    # Act
    move_error = movement.move(move_direction)
    player_position_result = movement.get_player_position()

    # Assert
    assert move_error is None
    assert player_position_result == starting_position


def test_move_when_given_valid_direction_to_know_tile_returns_none_and_does_not_turn_on_placement_mode() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=42)
    move_direction = Direction.SOUTH
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()

    # Act
    move_error = movement.move(move_direction)
    mode_value = movement.is_placement_mode_on()

    # Assert
    assert move_error is None
    assert mode_value is False


def test_move_when_given_valid_direction_to_known_tile_moves_player_to_tile() -> None:
    # Arrange
    new_player_position = (2, 1)
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2))
    move_direction = Direction.NORTH
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()
    movement.move(Direction.SOUTH)

    # Act
    move_error = movement.move(move_direction)
    player_position_result = movement.get_player_position()

    # Assert
    assert move_error is None
    assert player_position_result == new_player_position


# ========================== Bad Day ========================== #


@pytest.mark.parametrize("direction", ["UP", -1000, ()])
def test_move_when_given_invalid_direction_returns_direction_error(direction) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2))
    direction_error = ErrorCode.INVALID_VALUE_DIRECTION

    # Act
    move_error = movement.move(direction)

    # Assert
    assert move_error == direction_error


def test_move_when_given_invalid_direction_to_out_of_bounds_position_returns_out_of_bounds_error_and_does_not_move_player() -> None:
    # Arrange
    starting_position = (2, 0)
    movement = GameMap(map_dimensions=(5, 5), starting_position=starting_position, randomizer_seed=42)
    move_direction = Direction.NORTH
    out_of_bounds_error = ErrorCode.INVALID_MOVE_OUT_OF_BOUNDS

    # Act
    move_error = movement.move(move_direction)
    player_position = movement.get_player_position()

    # Assert
    assert move_error == out_of_bounds_error
    assert player_position == starting_position


def test_move_when_given_invalid_direction_to_empty_tile_with_no_door_returns_no_door_error_and_does_not_move_player() -> None:
    # Arrange
    starting_position = (2, 2)
    movement = GameMap(map_dimensions=(5, 5), starting_position=starting_position, randomizer_seed=42)
    move_direction = Direction.EAST
    door_error = ErrorCode.INVALID_MOVE_NO_DOOR

    # Act
    move_error = movement.move(move_direction)
    player_position = movement.get_player_position()

    # Assert
    assert move_error == door_error
    assert player_position == starting_position


def test_move_when_given_invalid_direction_to_known_tile_with_no_door_returns_no_door_error_and_does_not_move_player() -> None:
    # Arrange
    current_position = (1, 2)
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=42)
    move_direction = Direction.EAST
    door_error = ErrorCode.INVALID_MOVE_NO_DOOR
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()
    movement.move(Direction.WEST)
    movement.rotate_placement_tile()
    movement.lock_placement_tile()
    movement.move(Direction.SOUTH)
    movement.lock_placement_tile()

    # Act
    move_error = movement.move(move_direction)
    player_position = movement.get_player_position()

    # Assert
    assert move_error == door_error
    assert player_position == current_position


def test_move_when_given_invalid_direction_to_different_area_returns_across_area_error_and_does_not_move_player() -> None:
    # Arrange
    current_position = (1, 1)
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=1)
    move_direction = Direction.EAST
    cross_area_error = ErrorCode.INVALID_MOVE_ACROSS_AREAS
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()
    movement.move(Direction.WEST)
    movement.lock_placement_tile()
    movement.move(Direction.SOUTH)
    movement.lock_placement_tile()

    # Act
    move_error = movement.move(move_direction)
    player_position = movement.get_player_position()

    # Assert
    assert move_error == cross_area_error
    assert player_position == current_position


def test_move_to_new_inside_when_all_inside_explored_returns_depleted_inside_error_and_does_not_move_player() -> None:
    # Arrange
    current_position = (1, 4)
    movement = GameMap(map_dimensions=(5, 5), starting_position=(0, 4), randomizer_seed=4)
    move_direction = Direction.EAST
    depleted_inside_error = ErrorCode.DEPLETED_INSIDE_TILES
    movement.move(Direction.NORTH)
    movement.rotate_placement_tile()
    movement.rotate_placement_tile()
    movement.lock_placement_tile()
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()
    movement.move(Direction.EAST)
    movement.lock_placement_tile()
    movement.move(Direction.EAST)
    movement.lock_placement_tile()
    movement.move(Direction.WEST)
    movement.move(Direction.WEST)
    movement.move(Direction.SOUTH)
    movement.move(Direction.EAST)
    movement.rotate_placement_tile()
    movement.rotate_placement_tile()
    movement.lock_placement_tile()
    movement.move(Direction.EAST)
    movement.lock_placement_tile()
    movement.move(Direction.WEST)
    movement.move(Direction.SOUTH)
    movement.rotate_placement_tile()
    movement.lock_placement_tile()

    # Act
    move_error = movement.move(move_direction)
    player_position = movement.get_player_position()

    # Assert
    assert move_error == depleted_inside_error
    assert player_position == current_position


def test_move_to_new_outside_when_all_outside_explored_returns_depleted_outside_error_and_does_not_move_player() -> None:
    # Arrange
    current_position = (2, 1)
    movement = GameMap(map_dimensions=(4, 5), starting_position=(0, 4), randomizer_seed=1)
    move_direction = Direction.NORTH
    depleted_outside_error = ErrorCode.DEPLETED_OUTSIDE_TILES
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()
    movement.move(Direction.NORTH)
    movement.rotate_placement_tile()
    movement.lock_placement_tile()
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()
    movement.move(Direction.EAST)
    movement.rotate_placement_tile()
    movement.rotate_placement_tile()
    movement.lock_placement_tile()
    movement.move(Direction.SOUTH)
    movement.lock_placement_tile()
    movement.move(Direction.SOUTH)
    movement.lock_placement_tile()
    movement.move(Direction.EAST)
    movement.rotate_placement_tile()
    movement.lock_placement_tile()
    movement.move(Direction.NORTH)
    movement.rotate_placement_tile()
    movement.lock_placement_tile()

    # Act
    move_error = movement.move(move_direction)
    player_position = movement.get_player_position()

    # Assert
    assert move_error == depleted_outside_error
    assert player_position == current_position


def test_move_without_locking_tile_returns_placement_mode_error_and_does_not_move_player() -> None:
    # Arrange
    starting_position = (2, 2)
    movement = GameMap(map_dimensions=(5, 5), starting_position=starting_position, randomizer_seed=5)
    move_direction = Direction.NORTH
    placement_mode_error = ErrorCode.INVALID_ACTION_PLACEMENT_MODE_ON
    movement.move(Direction.NORTH)

    # Act
    move_error = movement.move(move_direction)
    player_position = movement.get_player_position()

    # Assert
    assert move_error == placement_mode_error
    assert player_position == starting_position


def test_move_when_player_actions_cause_unplaceable_tile_returns_fatal_tile_error_and_does_not_move_player() -> None:
    # Arrange
    current_position = (1, 4)
    movement = GameMap(map_dimensions=(5, 5), starting_position=(0, 3), randomizer_seed=7)
    move_direction = Direction.WEST
    unplaceable_error = ErrorCode.FATAL_UNPLACEABLE_TILE
    movement.move(Direction.NORTH)
    movement.rotate_placement_tile()
    movement.lock_placement_tile()
    movement.move(Direction.EAST)
    movement.rotate_placement_tile()
    movement.lock_placement_tile()
    movement.move(Direction.SOUTH)
    movement.rotate_placement_tile()
    movement.lock_placement_tile()
    movement.move(Direction.SOUTH)
    movement.lock_placement_tile()
    movement.create_zombie_door(Direction.WEST)

    # Act
    move_error = movement.move(move_direction)
    player_position = movement.get_player_position()

    # Assert
    assert move_error == unplaceable_error
    assert player_position == current_position

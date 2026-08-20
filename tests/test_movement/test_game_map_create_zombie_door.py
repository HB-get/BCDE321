import pytest

from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.direction import Direction
from zimp.domain.movement.game_map import GameMap


# ========================== Good Day ========================== #


def test_create_zombie_door_when_given_valid_direction_to_empty_tile_returns_none_and_creates_zombie_door_in_correct_direction() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=5)
    move_direction = Direction.EAST
    second_tile_id = 5
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()

    # Act
    move_error = movement.create_zombie_door(move_direction)
    tile_data = movement.get_tile_data()

    # Assert
    assert move_error is None
    assert any(tile.id == second_tile_id and tile.zombie_door == move_direction for tile in tile_data)


# ========================== Bad Day ========================== #


@pytest.mark.parametrize("direction", ["UP", -1000, ()])
def test_create_zombie_door_when_given_invalid_direction_returns_direction_error(direction) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2))
    direction_error = ErrorCode.INVALID_VALUE_DIRECTION

    # Act
    move_error = movement.create_zombie_door(direction)

    # Assert
    assert move_error == direction_error


def test_create_zombie_door_when_given_invalid_direction_to_out_of_bounds_position_returns_out_of_bounds_error_and_does_not_move_player() -> None:
    # Arrange
    starting_position = (2, 0)
    movement = GameMap(map_dimensions=(5, 5), starting_position=starting_position, randomizer_seed=42)
    move_direction = Direction.NORTH
    out_of_bounds_error = ErrorCode.INVALID_MOVE_OUT_OF_BOUNDS

    # Act
    move_error = movement.create_zombie_door(move_direction)
    player_position = movement.get_player_position()

    # Assert
    assert move_error == out_of_bounds_error
    assert player_position == starting_position


def test_create_zombie_door_when_given_invalid_direction_to_known_tile_returns_zombie_door_known_tile_error_and_does_not_move_player() -> None:
    # Arrange
    current_position = (2, 1)
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=5)
    move_direction = Direction.SOUTH
    zombie_door_error = ErrorCode.INVALID_MOVE_ZOMBIE_DOOR_TO_KNOWN_TILE
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()

    # Act
    move_error = movement.create_zombie_door(move_direction)
    player_position = movement.get_player_position()

    # Assert
    assert move_error == zombie_door_error
    assert player_position == current_position


def test_create_zombie_door_without_locking_tile_returns_placement_mode_error_and_does_not_move_player() -> None:
    # Arrange
    starting_position = (2, 2)
    movement = GameMap(map_dimensions=(5, 5), starting_position=starting_position, randomizer_seed=5)
    move_direction = Direction.NORTH
    placement_mode_error = ErrorCode.INVALID_ACTION_PLACEMENT_MODE_ON
    movement.move(Direction.NORTH)

    # Act
    move_error = movement.create_zombie_door(move_direction)
    player_position = movement.get_player_position()

    # Assert
    assert move_error == placement_mode_error
    assert player_position == starting_position

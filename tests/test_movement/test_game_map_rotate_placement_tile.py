from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.direction import Direction
from zimp.domain.movement.game_map import GameMap


# ========================== Good Day ========================== #


def test_rotate_placement_tile_doors_are_rotated_and_returns_none() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(4, 1), randomizer_seed=42)
    movement.move(Direction.NORTH)
    second_tile_id = 2
    first_rotation_direction = Direction.WEST
    second_rotation_direction = Direction.SOUTH

    # Act
    tile_data_one = movement.get_tile_data()
    rotate_result = movement.rotate_placement_tile()
    tile_data_two = movement.get_tile_data()

    # Assert
    assert rotate_result is None
    assert any(tile.id == second_tile_id and tile.rotation == first_rotation_direction for tile in tile_data_one)
    assert any(tile.id == second_tile_id and tile.rotation == second_rotation_direction for tile in tile_data_two)


def test_rotate_placement_tile_rotated_exit_door_transition_is_not_blocked() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(0, 4), randomizer_seed=1)
    movement.move(Direction.NORTH)
    second_tile_id = 3
    first_rotation_direction = Direction.NORTH
    second_rotation_direction = Direction.EAST
    third_rotation_direction = Direction.NORTH

    # Act
    tile_data_one = movement.get_tile_data()
    movement.rotate_placement_tile()
    tile_data_two = movement.get_tile_data()
    movement.rotate_placement_tile()
    tile_data_three = movement.get_tile_data()

    # Assert
    assert any(tile.id == second_tile_id and tile.rotation == first_rotation_direction for tile in tile_data_one)
    assert any(tile.id == second_tile_id and tile.rotation == second_rotation_direction for tile in tile_data_two)
    assert any(tile.id == second_tile_id and tile.rotation == third_rotation_direction for tile in tile_data_three)


def test_rotate_placement_tile_rotated_entry_door_transition_aligns_with_exit() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(4, 1), randomizer_seed=1)
    movement.move(Direction.NORTH)
    movement.rotate_placement_tile()
    movement.lock_placement_tile()
    movement.move(Direction.WEST)
    third_tile_id = 11
    rotation_direction = Direction.EAST

    # Act
    tile_data_one = movement.get_tile_data()
    movement.rotate_placement_tile()
    tile_data_two = movement.get_tile_data()

    # Assert
    assert any(tile.id == third_tile_id and tile.rotation == rotation_direction for tile in tile_data_one)
    assert any(tile.id == third_tile_id and tile.rotation == rotation_direction for tile in tile_data_two)


# ========================== Bad Day ========================== #


def test_rotate_placement_tile_rotating_locked_tile_returns_rotate_tile_error() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 4), starting_position=(4, 1), randomizer_seed=1)
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()
    rotate_tile_error = ErrorCode.INVALID_ACTION_ROTATE_LOCKED_TILE

    # Act
    rotate_result = movement.rotate_placement_tile()

    # Assert
    assert rotate_result == rotate_tile_error

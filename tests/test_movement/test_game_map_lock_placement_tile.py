from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.direction import Direction
from zimp.domain.movement.game_map import GameMap


# ========================== Good Day ========================== #


def test_lock_placement_tile_tile_is_locked_and_returns_none() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(4, 1), randomizer_seed=1)
    movement.move(Direction.NORTH)
    second_tile_id = 3

    # Act
    lock_result = movement.lock_placement_tile()
    tile_data = movement.get_tile_data()

    # Assert
    assert lock_result is None
    assert any(tile.id == second_tile_id and tile.is_locked for tile in tile_data)


def test_lock_placement_tile_player_is_moved_to_tile() -> None:
    # Arrange
    player_position = (1, 3)
    movement = GameMap(map_dimensions=(5, 5), starting_position=(1, 4), randomizer_seed=1)
    movement.move(Direction.NORTH)

    # Act
    movement.lock_placement_tile()
    result = movement.get_player_position()

    # Assert
    assert result == player_position


# ========================== Bad Day ========================== #


def test_lock_placement_tile_locking_a_locked_tile_returns_lock_tile_error() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 4), starting_position=(4, 1), randomizer_seed=1)
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()
    rotate_tile_error = ErrorCode.INVALID_ACTION_LOCK_LOCKED_TILE

    # Act
    rotate_result = movement.lock_placement_tile()

    # Assert
    assert rotate_result == rotate_tile_error

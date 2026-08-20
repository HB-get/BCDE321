import pytest

from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.direction import Direction
from zimp.domain.movement.game_map import GameMap


# ========================== Good Day ========================== #


def test_reset_when_given_valid_map_dimensions_sets_map_dimensions() -> None:
    # Arrange
    new_map_dimensions = (4, 4)
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2))

    # Act
    result = movement.reset(map_dimensions=new_map_dimensions)

    # Assert
    assert result is None
    assert movement.get_map_dimensions() == new_map_dimensions


def test_reset_when_given_no_map_dimensions_previous_map_dimensions_are_used() -> None:
    # Arrange
    map_dimensions = (4, 4)
    movement = GameMap(map_dimensions=map_dimensions, starting_position=(2, 2))

    # Act
    result = movement.reset()

    # Assert
    assert result is None
    assert movement.get_map_dimensions() == map_dimensions


def test_reset_when_given_valid_starting_position_sets_player_position() -> None:
    # Arrange
    new_starting_position = (1, 1)
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2))

    # Act
    result = movement.reset(starting_position=new_starting_position)

    # Assert
    assert result is None
    assert movement.get_player_position() == new_starting_position


def test_reset_when_given_no_starting_position_previous_map_dimensions_are_used() -> None:
    # Arrange
    starting_position = (1, 1)
    movement = GameMap(map_dimensions=(5, 5), starting_position=starting_position)

    # Act
    result = movement.reset()

    # Assert
    assert result is None
    assert movement.get_player_position() == starting_position


def test_reset_when_given_valid_seed_keeps_tile_order_consistent() -> None:
    # Arrange
    map_dimensions = (4, 5)
    starting_position = (2, 2)
    seed = 42
    move_direction = Direction.NORTH
    second_tile_id = 2
    movement = GameMap(map_dimensions=map_dimensions, starting_position=starting_position,
                       randomizer_seed=seed)
    movement.move(move_direction)
    tile_data_one = movement.get_tile_data()

    # Act
    result = movement.reset(randomizer_seed=seed)
    movement.move(move_direction)
    tile_data_two = movement.get_tile_data()

    # Assert
    assert result is None
    assert any(tile_data.id == second_tile_id for tile_data in tile_data_one)
    assert any(tile_data.id == second_tile_id for tile_data in tile_data_two)


def test_reset_clears_all_discovered_tiles() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(3, 3), randomizer_seed=42)
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()

    # Act
    result = movement.reset()

    # Assert
    assert len(movement.get_tile_data()) == 1
    assert result is None


# ========================== Bad Day ========================== #


@pytest.mark.parametrize("map_dimensions", [(4.1, 5.3), ("5", "5"), (4,), (4, 5, 5), [5, 5], {4, 4}])
def test_reset_when_given_invalid_map_dimensions_type_returns_map_dimensions_type_error(
        map_dimensions: tuple[int, int]) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 4), starting_position=(4, 1), randomizer_seed=1)
    map_dimensions_error = ErrorCode.INVALID_TYPE_MAP_DIMENSION

    # Act
    result = movement.reset(map_dimensions=map_dimensions)

    # Assert
    assert result == map_dimensions_error


@pytest.mark.parametrize("map_dimensions", [(0, 0), (-1, 3), (5, -1), (3, 4)])
def test_reset_when_given_invalid_map_dimensions_value_returns_map_dimensions_value_error(
        map_dimensions: tuple[int, int]) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 4), starting_position=(2, 1), randomizer_seed=1)
    map_dimensions_error = ErrorCode.INVALID_VALUE_MAP_DIMENSION

    # Act
    result = movement.reset(map_dimensions=map_dimensions)

    # Assert
    assert result == map_dimensions_error


@pytest.mark.parametrize("map_dimensions", [(2, 2), (2, 4), (4, 2), (4, 4)])
def test_reset_when_given_invalid_map_dimensions_with_existing_starting_position_returns_map_dimensions_value_error(
        map_dimensions: tuple[int, int]) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(4, 4), randomizer_seed=1)
    map_dimensions_error = ErrorCode.INVALID_VALUE_MAP_DIMENSION

    # Act
    result = movement.reset(map_dimensions=map_dimensions)

    # Assert
    assert result == map_dimensions_error


@pytest.mark.parametrize("starting_position", [(4.1, 5.3), ("5", "5"), (4,), (4, 5, 5), [5, 5], {4, 4}])
def test_reset_when_given_invalid_starting_position_type_returns_starting_position_type_error(
        starting_position: tuple[int, int]) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(4, 1), randomizer_seed=1)
    starting_position_error = ErrorCode.INVALID_TYPE_STARTING_POSITION

    # Act
    result = movement.reset(starting_position=starting_position)

    # Assert
    assert result == starting_position_error


@pytest.mark.parametrize("starting_position", [(-1, 3), (4, -1), (1, 5), (5, 1)])
def test_reset_when_given_invalid_starting_position_value_returns_starting_position_value_error(
        starting_position: tuple[int, int]) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(4, 1), randomizer_seed=1)
    starting_position_error = ErrorCode.INVALID_VALUE_STARTING_POSITION

    # Act
    result = movement.reset(starting_position=starting_position)

    # Assert
    assert result == starting_position_error


@pytest.mark.parametrize("starting_position", [(6, 6), (2, 6), (6, 2), (5, 5)])
def test_reset_when_given_invalid_starting_position_with_existing_map_dimensions_returns_starting_position_value_error(
        starting_position: tuple[int, int]) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(3, 3), randomizer_seed=1)
    starting_position_error = ErrorCode.INVALID_VALUE_STARTING_POSITION

    # Act
    result = movement.reset(starting_position=starting_position)

    # Assert
    assert result == starting_position_error


@pytest.mark.parametrize("map_dimensions, starting_position",
                         [((4, 4), (2, 4)), ((4, 4), (4, 2)), ((3, 3), (2, 2)), ((4, 4), (-1, -1))])
def test_reset_when_given_invalid_starting_position_and_map_dimensions_returns_starting_position_error(
        map_dimensions: tuple[int, int], starting_position: tuple[int, int]) -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(3, 3), randomizer_seed=1)
    starting_position_error = ErrorCode.INVALID_VALUE_STARTING_POSITION

    # Act
    result = movement.reset(map_dimensions=map_dimensions, starting_position=starting_position)

    # Assert
    assert result == starting_position_error


def test_reset_when_given_invalid_randomizer_seed_type_returns_randomizer_seed_type_error() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 4), starting_position=(4, 1), randomizer_seed=1)
    invalid_seed = "42"
    randomizer_seed_error = ErrorCode.INVALID_TYPE_RANDOMIZER_SEED

    # Act
    result = movement.reset(randomizer_seed=invalid_seed)

    # Assert
    assert result == randomizer_seed_error

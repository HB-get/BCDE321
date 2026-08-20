import pytest

from zimp.domain.common.direction import Direction
from zimp.domain.movement.game_map import GameMap


# ========================== Good Day ========================== #


def test_init_when_given_valid_map_dimensions_sets_map_dimensions() -> None:
    # Arrange
    map_dimensions = (4, 5)

    # Act
    movement = GameMap(map_dimensions=map_dimensions, starting_position=(2, 2))

    # Assert
    assert movement.get_map_dimensions() == map_dimensions


def test_init_when_given_valid_starting_position_sets_player_position() -> None:
    # Arrange
    starting_position = (2, 2)

    # Act
    movement = GameMap(map_dimensions=(4, 5), starting_position=starting_position)

    # Assert
    assert movement.get_player_position() == starting_position


def test_init_when_given_valid_seed_keeps_tile_order_consistent() -> None:
    # Arrange
    map_dimensions = (4, 5)
    starting_position = (2, 2)
    seed = 42
    move_direction = Direction.NORTH
    second_tile_id = 2

    # Act
    movement_one = GameMap(map_dimensions=map_dimensions, starting_position=starting_position,
                           randomizer_seed=seed)
    movement_one.move(move_direction)
    tile_data_one = movement_one.get_tile_data()
    movement_two = GameMap(map_dimensions=map_dimensions, starting_position=starting_position,
                           randomizer_seed=seed)
    movement_two.move(move_direction)
    tile_data_two = movement_two.get_tile_data()

    # Assert
    assert any(tile_data.id == second_tile_id for tile_data in tile_data_one)
    assert any(tile_data.id == second_tile_id for tile_data in tile_data_two)


def test_init_when_given_no_map_dimensions_default_map_dimensions_is_used() -> None:
    # Arrange
    default_map_dimensions = (5, 5)

    # Act
    movement = GameMap(starting_position=(2, 4))

    # Assert
    assert movement.get_map_dimensions() == default_map_dimensions


def test_init_when_given_no_starting_position_default_starting_position_is_used() -> None:
    # Arrange
    default_starting_position = (2, 4)

    # Act
    movement = GameMap(map_dimensions=(5, 5))

    # Assert
    assert movement.get_player_position() == default_starting_position


# ========================== Bad Day ========================== #


@pytest.mark.parametrize("map_dimensions", [(4.1, 5.3), ("5", "5"), (4,), (4, 5, 5), [5, 5], {4, 4}])
def test_init_when_given_invalid_map_dimensions_type_raises_type_error_with_correct_message(
        map_dimensions: tuple[int, int]) -> None:
    # Arrange
    starting_position = (2, 2)

    # Act & Assert
    with pytest.raises(TypeError, match="Invalid map dimensions type, must be a tuple of two integers"):
        GameMap(map_dimensions=map_dimensions, starting_position=starting_position)


@pytest.mark.parametrize("map_dimensions", [(0, 0), (-1, 3), (5, -1), (1, 1)])
def test_init_when_given_invalid_map_dimensions_value_raises_value_error_with_correct_message(
        map_dimensions: tuple[int, int]) -> None:
    # Arrange
    starting_position = (2, 2)

    # Act & Assert
    with pytest.raises(ValueError, match="Map dimensions must be greater than 4x4"):
        GameMap(map_dimensions=map_dimensions, starting_position=starting_position)


@pytest.mark.parametrize("starting_position", [(4.1, 5.3), ("5", "5"), (4,), (4, 5, 5), [5, 5], {4, 4}])
def test_init_when_given_invalid_starting_position_type_raises_type_error_with_correct_message(
        starting_position: tuple[int, int]) -> None:
    # Arrange
    map_dimensions = (4, 5)

    # Act & Assert
    with pytest.raises(TypeError, match="Invalid starting position type, must be a tuple of two integers"):
        GameMap(map_dimensions=map_dimensions, starting_position=starting_position)


@pytest.mark.parametrize("starting_position", [(-1, 3), (5, -1), (4, 5)])
def test_init_when_given_invalid_starting_position_value_raises_value_error_with_correct_message(
        starting_position: tuple[int, int]) -> None:
    # Arrange
    map_dimensions = (4, 5)

    # Act & Assert
    with pytest.raises(ValueError, match="Starting position must be within the map dimensions"):
        GameMap(map_dimensions=map_dimensions, starting_position=starting_position)


def test_init_when_given_invalid_randomizer_seed_value_raises_value_error_with_correct_message() -> None:
    # Arrange
    map_dimensions = (4, 5)
    starting_position = (2, 2)
    invalid_seed = "42"

    # Act & Assert
    with pytest.raises(TypeError, match="Randomizer seed must be an integer"):
        GameMap(map_dimensions=map_dimensions, starting_position=starting_position, randomizer_seed=invalid_seed)

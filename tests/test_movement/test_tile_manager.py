from zimp.domain.common.error_code import ErrorCode
from zimp.domain.movement.tile_manager import TileManager


# ========================== Good Day ========================== #


def test_set_randomizer_seed_when_given_valid_value_returns_none() -> None:
    # Arrange
    tile_manager = TileManager()
    invalid_seed = 42

    # Act
    result = tile_manager.reset_tile_order(invalid_seed)

    # Assert
    assert result is None


def test_set_randomizer_seed_when_given_valid_value_keeps_tile_order_consistent() -> None:
    # Arrange
    tile_manager = TileManager()
    seed = 42
    tile_manager.reset_tile_order(seed)
    second_inside_tile_id = 2
    second_outside_tile_id = 10
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_outside_tile()

    # Act
    inside_result = tile_manager.get_next_inside_tile()
    outside_result = tile_manager.get_next_outside_tile()

    # Assert
    assert inside_result.is_fail() is False
    assert outside_result.is_fail() is False
    assert inside_result.get_data().get_data((0, 0)).id == second_inside_tile_id
    assert outside_result.get_data().get_data((0, 0)).id == second_outside_tile_id


def test_is_inside_tiles_depleted_when_tiles_left_returns_false() -> None:
    # Arrange
    tile_manager = TileManager()

    # Act
    result = tile_manager.is_inside_tiles_depleted()

    # Assert
    assert result is False


def test_is_inside_tiles_depleted_when_no_tiles_left_returns_true() -> None:
    # Arrange
    tile_manager = TileManager()
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_inside_tile()

    # Act
    result = tile_manager.is_inside_tiles_depleted()

    # Assert
    assert result is True


def test_is_outside_tiles_depleted_when_tiles_left_returns_false() -> None:
    # Arrange
    tile_manager = TileManager()

    # Act
    result = tile_manager.is_outside_tiles_depleted()

    # Assert
    assert result is False


def test_is_outside_tiles_depleted_when_no_tiles_left_returns_true() -> None:
    # Arrange
    tile_manager = TileManager()
    tile_manager.get_next_outside_tile()
    tile_manager.get_next_outside_tile()
    tile_manager.get_next_outside_tile()
    tile_manager.get_next_outside_tile()
    tile_manager.get_next_outside_tile()
    tile_manager.get_next_outside_tile()
    tile_manager.get_next_outside_tile()
    tile_manager.get_next_outside_tile()

    # Act
    result = tile_manager.is_outside_tiles_depleted()

    # Assert
    assert result is True


def test_get_next_inside_tile_when_no_tiles_left_returns_depleted_outside_error() -> None:
    # Arrange
    tile_manager = TileManager()
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_inside_tile()
    tile_manager.get_next_inside_tile()
    depleted_error = ErrorCode.DEPLETED_INSIDE_TILES

    # Act
    result = tile_manager.get_next_inside_tile()

    # Assert
    assert result.is_fail() is True
    assert result.get_error_code() == depleted_error


def test_get_next_outside_tile_when_no_tiles_left_returns_depleted_outside_error() -> None:
    # Arrange
    tile_manager = TileManager()
    tile_manager.get_next_outside_tile()
    tile_manager.get_next_outside_tile()
    tile_manager.get_next_outside_tile()
    tile_manager.get_next_outside_tile()
    tile_manager.get_next_outside_tile()
    tile_manager.get_next_outside_tile()
    tile_manager.get_next_outside_tile()
    tile_manager.get_next_outside_tile()
    depleted_error = ErrorCode.DEPLETED_OUTSIDE_TILES

    # Act
    result = tile_manager.get_next_outside_tile()

    # Assert
    assert result.is_fail() is True
    assert result.get_error_code() == depleted_error


# ========================== Bad Day ========================== #

def test_set_randomizer_seed_when_given_invalid_value_returns_randomizer_seed_error() -> None:
    # Arrange
    tile_manager = TileManager()
    invalid_seed = "42"
    randomizer_seed_error = ErrorCode.INVALID_TYPE_RANDOMIZER_SEED

    # Act
    result = tile_manager.reset_tile_order(invalid_seed)

    # Assert
    assert result == randomizer_seed_error

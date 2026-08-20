from zimp.domain.common.direction import Direction
from zimp.domain.movement.game_map import GameMap


# ========================== Good Day ========================== #


def test_need_zombie_door_when_normal_door_open_to_empty_tile_returns_false() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=42)

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is False


def test_need_zombie_door_when_no_normal_door_open_to_empty_tile_returns_true() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(2, 2), randomizer_seed=5)
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is True


# ========================== Bad Day ========================== #


def test_need_zombie_door_when_only_normal_door_open_to_out_of_bounds_returns_true() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(0, 2), randomizer_seed=42)
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is True


def test_need_zombie_door_when_only_open_door_is_exit_door_returns_true() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(0, 2), randomizer_seed=1)
    movement.move(Direction.NORTH)
    movement.lock_placement_tile()
    movement.move(Direction.EAST)
    movement.lock_placement_tile()

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is True


def test_need_zombie_door_when_no_open_normal_door_and_all_insides_explored_returns_false() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(0, 4), randomizer_seed=4)
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
    movement.lock_placement_tile()

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is False


def test_need_zombie_door_when_no_open_normal_door_and_all_outsides_explored_returns_false() -> None:
    # Arrange
    movement = GameMap(map_dimensions=(5, 5), starting_position=(0, 4), randomizer_seed=1)
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
    movement.lock_placement_tile()

    # Act
    z_door_result = movement.need_zombie_door()

    # Assert
    assert z_door_result is False

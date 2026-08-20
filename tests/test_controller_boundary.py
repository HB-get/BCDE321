from zimp.domain.common.direction import Direction
from zimp.integration.game_controller import GameController


class FakeGame:
    def __init__(self, result=None) -> None:
        self.result = result
        self.calls = []

    def reset(self) -> None:
        self.calls.append(("reset",))

    def move_player(self, direction: Direction):
        self.calls.append(("move_player", direction))
        return self.result


def test_controller_calls_game_for_up_movement() -> None:
    fake = FakeGame()

    result = GameController(fake).move_up()

    assert result == "Moved up."
    assert fake.calls == [("move_player", Direction.NORTH)]


def test_controller_calls_game_for_down_movement() -> None:
    fake = FakeGame()

    result = GameController(fake).move_down()

    assert result == "Moved down."
    assert fake.calls == [("move_player", Direction.SOUTH)]


def test_controller_calls_game_for_left_movement() -> None:
    fake = FakeGame()

    result = GameController(fake).move_left()

    assert result == "Moved left."
    assert fake.calls == [("move_player", Direction.WEST)]


def test_controller_calls_game_for_right_movement() -> None:
    fake = FakeGame()

    result = GameController(fake).move_right()

    assert result == "Moved right."
    assert fake.calls == [("move_player", Direction.EAST)]


def test_controller_returns_game_error_for_failed_movement() -> None:
    fake = FakeGame("INVALID_MOVE_NO_DOOR")

    result = GameController(fake).move_up()

    assert result == "INVALID_MOVE_NO_DOOR"
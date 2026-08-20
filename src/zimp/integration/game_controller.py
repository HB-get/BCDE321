from zimp.domain.common.contract_game import GameContract
from zimp.domain.common.direction import Direction


class GameController:
    """Thin, testable boundary between Tkinter events and domain behaviour."""

    def __init__(self, game: GameContract) -> None:
        self._game = game

    def reset(self) -> str:
        self._game.reset()
        return "Game reset."

    def move_up(self) -> str:
        result = self._game.move_player(Direction.NORTH)

        if result is None:
            return "Moved up."

        return str(result)

    def move_down(self) -> str:
        result = self._game.move_player(Direction.SOUTH)

        if result is None:
            return "Moved down."

        return str(result)

    def move_left(self) -> str:
        result = self._game.move_player(Direction.WEST)

        if result is None:
            return "Moved left."

        return str(result)

    def move_right(self) -> str:
        result = self._game.move_player(Direction.EAST)

        if result is None:
            return "Moved right."

        return str(result)
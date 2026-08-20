from zimp.domain.game_state.game_state import GameState


class BasicMovement:
    """Illustrative contract implementation.

    This class exists to make the walking skeleton executable. It is not a
    model solution for an assessed student feature.
    """

    VALID_DIRECTIONS = frozenset({"north", "south", "east", "west"})

    def __init__(self, state: GameState) -> None:
        self._state = state

    def move(self, direction: str) -> str:
        normalised = direction.strip().lower()
        if normalised not in self.VALID_DIRECTIONS:
            raise ValueError(f"Unsupported direction: {direction}")
        self._state.last_move = normalised
        self._state.turn_number += 1
        return f"Moved {normalised}. Turn {self._state.turn_number}."

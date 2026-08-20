from zimp.domain.contracts import MovementGateway


class GameController:
    """Thin, testable boundary between Tkinter events and domain behaviour."""

    def __init__(self, movement: MovementGateway) -> None:
        self._movement = movement

    def handle_move(self, direction: str) -> str:
        """Handle a movement request from the UI."""
        direction = direction.strip().lower()

        if direction not in {"north", "south", "east", "west"}:
            return f"Cannot move: invalid direction '{direction}'."

        try:
            return self._movement.move(direction)
        except ValueError as error:
            return f"Cannot move: {error}"
        except RuntimeError:
            return "Cannot move: the movement component is currently unavailable."
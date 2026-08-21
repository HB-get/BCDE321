from typing import Protocol, runtime_checkable


@runtime_checkable
class MovementGateway(Protocol):
    """Contract used by the application layer to request map.

    Student work may implement this contract or consume it at an assessed
    integration boundary. Do not couple implementations to Tkinter widgets.
    """

    def move(self, direction: str) -> str:
        """Apply a map command and return a user-facing status message."""

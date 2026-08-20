from typing import Protocol, runtime_checkable
from zimp.domain.common.mode import Mode

@runtime_checkable
class GameStateContract(Protocol):
    """Contract used by the application layer to request changes to the Game State."""
    def reset(self) -> None:
        """Reset the game state for a new game."""
    def advance_time(self, hours: int = 1) -> None:
        """Advance the game time by 1 hour."""
    def change_hp(self, amount: int) -> None:
        """Change the player HP by a specified amount."""
    def take_totem(self) -> None:
        """Player picks up the totem"""
    def bury_totem(self) -> None:
        """Player buries the totem"""
    def cower(self) -> tuple[int, bool]:
        """Player cowers"""
    def is_won(self) -> bool:
        """Game is won"""
    def is_lost(self) -> bool:
        """Game is lost"""
    def get_hp(self) -> str:
        """Return current player HP value"""
    def get_attack(self) -> str:
        """Return current player attack value"""
    def get_stats(self) -> str:
        """Return current player stats summary"""
    def get_time(self) -> str:
        """Return current game time"""
    def has_got_totem(self) -> bool:
        """Tracks whether the player has the totem"""
    def set_mode(self, new_mode: Mode) -> None:
        """Set the current game mode"""
    def check_win_loss(self) -> Mode:
        """Checks if the game is won or lost"""

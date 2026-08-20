from typing import Protocol, runtime_checkable
from zimp.domain.common.result import Result

@runtime_checkable
class EventsContract(Protocol):
    """Contract used by the application layer to resolve player events."""

    def reset(self) -> None:
        """Reset the deck"""
    def get_remaining_card_count(self):
        """Get the number of dev cards currently in the deck"""
    def draw_event(self, time: int) -> tuple[Result, bool]:
        """Draw a dev card from the deck and return the effect, shuffling if required"""
    def draw_item(self) -> tuple[Result, bool]:
        """Draw a dev card from the deck and return the item, shuffling if required"""
    def waste_time(self) -> tuple[Result, bool]:
        """Discard a card"""
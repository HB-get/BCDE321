from typing import Protocol, runtime_checkable

from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.item_code import ItemCode
from zimp.domain.common.result import Result


@runtime_checkable
class ItemsContract(Protocol):
    """Contract used by the application layer to reach the player's inventory.

    Illegal actions raise ValueError carrying a message meant for the player;
    the controller turns that into visible text rather than handling codes.
    """

    def reset(self) -> None:
        """Reset the inventory to its initial state"""

    def record_battle(self) -> None: #unchanged
        """Tell the inventory a battle happened so the chainsaw burns fuel.

        Combat must call this or the chainsaw never runs out.
        """
    # New methods
    def attack_bonus(self, with_chainsaw: bool) -> Result: #updated
        """return the current attack bonus (Result.success(bonus).
        If with_chainsaw is true but you either dont have the chainsaw
        or it has no fuel, return Result.fail(ErrorCode.NO_CHAINSAW)"""

    def held_items(self) -> tuple[ItemCode, ItemCode]: #updated
        """Return the held items as a 2-tuple"""
    def get_has_instant_kill(self) -> bool:
        """Return whether inventory contains candle and either gasoline or oil"""
    def get_has_oil(self) -> bool:
        """return True/False whether oil is in the inventory"""
    def find_item(self, item_id: ItemCode) -> None:
        """Store internally a found item (like one that you can decide to keep or not"""
    def keep_found_item(self) -> ErrorCode | None:
        """try to add the "find item" item to the inventory.
        If there's no space, return ErrorCode.NO_SPACE
        if there's no found item, return ErrorCode.NO_FOUND_ITEM
        Otherwise return None"""
    def dont_take_item(self) -> None:
        """clear the stored found item"""
    def discard(self, slot_id: int) -> ErrorCode | None:
        """discard the item in slot_id (0 or 1)
        return ErrorCode.SLOT_EMPTY if slot is empty, else None
        """
    def use(self, item_id: ItemCode) -> ErrorCode | None:
        """can only be soda or gasoline. If they're present remove them and return None
        Otherwise return Result.fail(ErrorCode.NO_GASOLINE/NO_SODA)"""
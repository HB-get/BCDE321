"""The seam between the game orchestrator and the player's pockets.

Two components want the inventory in two different vocabularies. The Tkinter
shell, through `GameController`, speaks item names, takes back an `Effect`
receipt, and reads a refusal as a raised `ValueError`. The `Game` object
speaks `ItemCode`, and reads a refusal as a returned `ErrorCode` -- or a
`Result`, where a value has to come back with it.

Rather than teach either side the other's words, the translation lives here,
at the boundary, in the same spirit as returning an `Effect` instead of
reaching into another component's state. `Inventory` stays the one place the
item rules are written; this class only restates its answers.
"""

from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.item_code import ItemCode
from zimp.domain.common.item_ids import ID_FOR_ITEM_CODE, ITEM_CODE_FOR_ID
from zimp.domain.common.result import Result
from zimp.domain.items.inventory import Inventory

# Which refusal to report when a usable item is not being carried. Every
# other item is not usable at all.
_MISSING = {
    ItemCode.SODA: ErrorCode.NO_SODA,
    ItemCode.GASOLINE: ErrorCode.NO_GASOLINE,
}


class GameItems:
    """The inventory, as the `Game` object expects to find it."""

    POCKETS = Inventory.CAPACITY

    def __init__(self, inventory: Inventory | None = None) -> None:
        self._inventory = inventory if inventory is not None else Inventory()
        # An item that has been found but not yet accepted. It is not in a
        # pocket, so it lives here rather than in the inventory.
        self._found: ItemCode | None = None

    def reset(self) -> None:
        self._inventory = Inventory()
        self._found = None

    def record_battle(self) -> None:
        self._inventory.record_battle()

    def attack_bonus(self, with_chainsaw: bool) -> Result:
        if with_chainsaw and not self._chainsaw_is_ready():
            return Result.fail(ErrorCode.NO_CHAINSAW)
        return Result.success(
            self._inventory.attack_bonus(include_chainsaw=with_chainsaw)
        )

    def held_items(self) -> tuple[ItemCode, ItemCode]:
        """Both pockets, in order. An empty pocket reads as `ItemCode.NONE`."""
        codes = [ITEM_CODE_FOR_ID[item_id] for item_id in self._inventory.held_items()]
        codes += [ItemCode.NONE] * (self.POCKETS - len(codes))
        return tuple(codes)

    def get_has_oil(self) -> bool:
        return self._carrying(ItemCode.OIL)

    def get_has_instant_kill(self) -> bool:
        """A candle plus something to burn wipes a tile clean."""
        return self._carrying(ItemCode.CANDLE) and (
            self._carrying(ItemCode.GASOLINE) or self._carrying(ItemCode.OIL)
        )

    def find_item(self, item_id: ItemCode) -> None:
        self._found = item_id

    def keep_found_item(self) -> ErrorCode | None:
        # `ItemCode.NONE` is the deck saying the search turned up nothing.
        # It is not an item, and it has no name to add.
        if self._found is None or self._found is ItemCode.NONE:
            return ErrorCode.NO_FOUND_ITEM
        try:
            self._inventory.add(ID_FOR_ITEM_CODE[self._found])
        except ValueError:
            # Keep holding it -- a pocket may free up before the player moves on.
            return ErrorCode.NO_SPACE
        self._found = None
        return None

    def dont_take_item(self) -> None:
        self._found = None

    def discard(self, slot_id: int) -> ErrorCode | None:
        try:
            self._inventory.discard_slot(slot_id)
        except ValueError:
            return ErrorCode.SLOT_EMPTY
        return None

    def use(self, item_id: ItemCode) -> ErrorCode | None:
        if item_id not in _MISSING:
            # Weapons are passive: carried, never used. Oil is the same --
            # it is not something the player uses on its own.
            return ErrorCode.FATAL_ERROR
        if not self._carrying(item_id):
            return _MISSING[item_id]

        name = ID_FOR_ITEM_CODE[item_id]
        if item_id is ItemCode.SODA:
            # The Effect receipt is dropped here: Game applies the healing
            # itself. The Tkinter path still reads it.
            self._inventory.use(name)
        else:
            if not self._carrying(ItemCode.CHAINSAW):
                # Gasoline only does anything in a chainsaw. Spending the
                # can with nothing to pour it into helps nobody.
                return ErrorCode.NO_CHAINSAW
            self._inventory.discard(name)
            self._inventory.refuel_chainsaw()
        return None

    def _carrying(self, item_id: ItemCode) -> bool:
        return ID_FOR_ITEM_CODE[item_id] in self._inventory.held_items()

    def _chainsaw_is_ready(self) -> bool:
        return self._carrying(ItemCode.CHAINSAW) and self._inventory.chainsaw_fuel > 0

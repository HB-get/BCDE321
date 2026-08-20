from typing import Protocol, runtime_checkable

from zimp.domain.items.inventory import Effect


@runtime_checkable
class InventoryContract(Protocol):
    """Contract the Tkinter path uses to reach the player's inventory.

    Illegal actions raise ValueError carrying a message meant for the player;
    the controller turns that into visible text rather than handling codes.
    """

    def add(self, item_id: str) -> None:
        """Take an item into the inventory, or refuse if both pockets are full."""

    def discard(self, item_id: str) -> None:
        """Drop a held item, or refuse if it is not held."""

    def use(self, item_id: str) -> Effect:
        """Spend a held consumable and report what should happen to the player."""

    def held_items(self) -> list[str]:
        """What the player is carrying."""

    def attack_bonus(self) -> int:
        """The attack a held weapon adds, counting only the best single weapon.

        Combat adds this to the player's base attack. An empty chainsaw
        contributes nothing.
        """

    def record_battle(self) -> None:
        """Tell the inventory a battle happened so the chainsaw burns fuel.

        Combat must call this or the chainsaw never runs out.
        """

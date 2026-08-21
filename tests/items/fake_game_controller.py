from zimp.domain.common.contract_inventory import ContractInventory
from zimp.domain.contracts import MovementGateway
from zimp.domain.items.inventory import Effect


class FakeGameController:
    """Fake for game controller, used for items boundary testing."""

    def __init__(self, movement: MovementGateway, items: ContractInventory) -> None:
        self._movement = movement
        self._items = items

    def handle_move(self, direction: str) -> str:
        try:
            return self._movement.move(direction)
        except ValueError as error:
            return f"Cannot move: {error}"
        except RuntimeError:
            return "Cannot move: the map component is currently unavailable."

    def handle_pick_up_item(self, item_id: str) -> str:
        try:
            self._items.add(item_id)
        except ValueError as error:
            return f"Cannot pick up: {error}"
        except RuntimeError:
            return "Cannot pick up: the items component is currently unavailable."
        return f"Picked up a {item_id}."

    def handle_use_item(self, item_id: str) -> str:
        try:
            effect = self._items.use(item_id)
        except ValueError as error:
            return f"Cannot use: {error}"
        except RuntimeError:
            return "Cannot use: the items component is currently unavailable."
        return " ".join([f"Used a {item_id}.", *_describe(effect)])

    def handle_discard_item(self, item_id: str) -> str:
        try:
            self._items.discard(item_id)
        except ValueError as error:
            return f"Cannot drop: {error}"
        except RuntimeError:
            return "Cannot drop: the items component is currently unavailable."
        return f"Dropped a {item_id}."

    def held_items(self) -> list[str]:
        """What to display as carried. An unavailable inventory shows as empty."""
        try:
            return self._items.held_items()
        except RuntimeError:
            return []


def _describe(effect: Effect) -> list[str]:
    """Turn an Effect into sentences, skipping the parts that change nothing."""
    changes = (("Health", effect.health), ("Attack", effect.attack))
    return [f"{name} {amount:+d}." for name, amount in changes if amount]

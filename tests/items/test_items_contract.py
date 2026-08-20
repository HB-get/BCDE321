"""Two contracts, because there are two consumers.

`ItemsContract` is Hayden's: the eleven methods `Game` calls, speaking
`ItemCode` in and `ErrorCode` out. `InventoryContract` is the Tkinter
path's: item names in, an `Effect` back, a `ValueError` on refusal.

`runtime_checkable` compares method names and nothing else -- not
arguments, not return types. Passing here means nothing was renamed or
dropped. It does not mean the signatures agree.
"""

from zimp.domain.common.contract_inventory import InventoryContract
from zimp.domain.common.contract_items import ItemsContract
from zimp.domain.items.game_items import GameItems
from zimp.domain.items.inventory import Inventory
from zimp.support.items.fake_items import FakeItemsGateway


def test_game_items_satisfies_the_game_contract() -> None:
    assert isinstance(GameItems(), ItemsContract)


def test_real_and_fake_satisfy_the_inventory_contract() -> None:
    assert isinstance(Inventory(), InventoryContract)
    assert isinstance(FakeItemsGateway(), InventoryContract)

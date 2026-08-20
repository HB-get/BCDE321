"""Where the dev-card deck's numbers and the inventory's names meet.

The deck reports a found item as a number (`DevCard.item`). The inventory
works in names (`"machete"`). Neither side should have to learn the other's
vocabulary, so the translation lives here and is applied once, at the
boundary, in the same spirit as returning an `Effect` instead of reaching
into another component's state.

Owned by items. Consumed by whoever resolves a SEARCH_FOR_ITEM result.
"""

from zimp.domain.common.item_code import ItemCode

# The nine items the rulebook defines. This is the inventory's vocabulary:
# every id the rest of the game may hand to `InventoryContract.add`.
#
# Being listed here does not mean the inventory gives the item behaviour --
# see IMPLEMENTED_ITEMS. An unimplemented item is carried, cannot be used,
# and grants no attack bonus.
RULEBOOK_ITEMS: tuple[str, ...] = (
    "board_with_nails",
    "can_of_soda",
    "candle",
    "chainsaw",
    "gasoline",
    "golf_club",
    "grisly_femur",
    "machete",
    "oil",
)

# The subset the inventory currently has rules for. Kept explicit so the gap
# between "a name exists" and "the name does something" stays visible.
IMPLEMENTED_ITEMS: frozenset[str] = frozenset(
    {
        "can_of_soda",
        "chainsaw",
        "golf_club",
        "machete",
    }
)

# Deck number -> inventory item id.
#
# DELIBERATELY EMPTY. The deck numbers its items 0-8, but which number the
# cards give to which item is not recorded anywhere in this repository, and a
# wrong guess here would fail silently: every id resolves to *a* valid item,
# so the game would run and simply hand out the wrong equipment.
#
# Fill this in from the physical cards, then delete this comment. Until then
# `item_id_for_card` refuses loudly, which is the failure we want.
CARD_ITEM_IDS: dict[int, str] = {}


# ItemCode -> inventory item id.
#
# Hayden's Game speaks `ItemCode`; the inventory holds names. This pair of
# dictionaries is the entire translation, and it is the only place in Items
# that knows another component's vocabulary.
#
# `ItemCode.NONE` is deliberately absent: it means "this pocket is empty",
# not "this item", so it must never resolve to a name.
ID_FOR_ITEM_CODE: dict[ItemCode, str] = {
    ItemCode.OIL: "oil",
    ItemCode.GASOLINE: "gasoline",
    ItemCode.BOARD_WITH_NAILS: "board_with_nails",
    ItemCode.MACHETE: "machete",
    ItemCode.GRISLY_FEMUR: "grisly_femur",
    ItemCode.GOLF_CLUB: "golf_club",
    ItemCode.CHAINSAW: "chainsaw",
    # The one place the two vocabularies disagree.
    ItemCode.SODA: "can_of_soda",
    ItemCode.CANDLE: "candle",
}

ITEM_CODE_FOR_ID: dict[str, ItemCode] = {
    item_id: code for code, item_id in ID_FOR_ITEM_CODE.items()
}


def item_id_for_card(card_item: int) -> str:
    """Translate a deck item number into an inventory item id.

    Raises ValueError while the mapping is incomplete, so an unmapped card
    stops the caller instead of quietly producing the wrong item.
    """
    if card_item not in CARD_ITEM_IDS:
        raise ValueError(
            f"card item {card_item} is not mapped to an inventory item; "
            f"fill CARD_ITEM_IDS in {__name__} from the dev cards"
        )
    return CARD_ITEM_IDS[card_item]
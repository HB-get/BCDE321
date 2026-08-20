from zimp.domain.common.dev_card import DevCard, CardEffect, CardEffectType
from zimp.domain.common.item_code import ItemCode

CARD_DATA = (
    DevCard(
        (CardEffect(CardEffectType.NONE),
        CardEffect(CardEffectType.ITEM),
        CardEffect(CardEffectType.ZOMBIES, 6)),
        ItemCode.OIL,
    ),
    DevCard(
        (CardEffect(CardEffectType.ZOMBIES, 4),
        CardEffect(CardEffectType.HEALTH, -1),
        CardEffect(CardEffectType.ITEM)),
        ItemCode.GASOLINE,
    ),
    DevCard(
        (CardEffect(CardEffectType.ITEM),
        CardEffect(CardEffectType.ZOMBIES, 4),
        CardEffect(CardEffectType.HEALTH, -1)),
        ItemCode.BOARD_WITH_NAILS,
    ),
    DevCard(
        (CardEffect(CardEffectType.ZOMBIES, 4),
        CardEffect(CardEffectType.HEALTH, -1),
        CardEffect(CardEffectType.ZOMBIES, 6)),
        ItemCode.MACHETE,
    ),
    DevCard(
        (CardEffect(CardEffectType.ITEM),
        CardEffect(CardEffectType.ZOMBIES, 5),
        CardEffect(CardEffectType.HEALTH, -1)),
        ItemCode.GRISLY_FEMUR,
    ),
    DevCard(
        (CardEffect(CardEffectType.HEALTH, -1),
        CardEffect(CardEffectType.ZOMBIES, 4),
        CardEffect(CardEffectType.NONE)),
        ItemCode.GOLF_CLUB,
    ),
    DevCard(
        (CardEffect(CardEffectType.ZOMBIES, 3),
        CardEffect(CardEffectType.NONE),
        CardEffect(CardEffectType.ZOMBIES, 5)),
        ItemCode.CHAINSAW,
    ),
    DevCard(
        (CardEffect(CardEffectType.HEALTH, 1),
        CardEffect(CardEffectType.ITEM),
        CardEffect(CardEffectType.ZOMBIES, 4)),
        ItemCode.SODA,
    ),
    DevCard(
        (CardEffect(CardEffectType.NONE),
        CardEffect(CardEffectType.HEALTH, 1),
        CardEffect(CardEffectType.ZOMBIES, 4)),
        ItemCode.CANDLE,
    ),
)
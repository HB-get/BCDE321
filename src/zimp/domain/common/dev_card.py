from dataclasses import dataclass
from enum import Enum, auto

from zimp.domain.common.item_code import ItemCode


class CardEffectType(Enum):
    NONE = auto()
    HEALTH = auto()
    ZOMBIES = auto()
    ITEM = auto()

@dataclass(frozen=True)
class CardEffect:
    effect_type: CardEffectType
    value: int = 0

@dataclass(frozen=True)
class DevCard:
    effects: tuple[CardEffect, CardEffect, CardEffect]
    item: ItemCode
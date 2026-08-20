from enum import Enum, auto

class Mode(Enum):
    NONE = auto()
    PLACE = auto()
    ZOMBIE_DOOR = auto()
    DEV_CARD = auto()
    COMBAT = auto()
    SEARCH_FOR_ITEM = auto()
    FOUND_ITEM = auto()
    WON = auto()
    LOST = auto()
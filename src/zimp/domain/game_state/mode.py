from enum import Enum, auto

class Mode(Enum):
    NONE = auto()
    MOVE = auto()
    ZOMBIE_DOOR = auto()
    DEV_CARD = auto()
    COMBAT = auto()
    ITEM_SEARCH = auto()
    ITEM_FOUND = auto()
    EVENTS_FINISHED = auto()
    WON = auto()
    LOST = auto()
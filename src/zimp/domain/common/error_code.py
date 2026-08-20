from enum import Enum, auto


class ErrorCode(Enum):
    """MOVEMENT ERRORS"""
    DEPLETED_INSIDE_TILES = auto()
    DEPLETED_OUTSIDE_TILES = auto()
    INVALID_POSITION = auto()
    INVALID_ACTION_ROTATE_LOCKED_TILE = auto()
    INVALID_ACTION_LOCK_LOCKED_TILE = auto()
    INVALID_ACTION_PLACEMENT_MODE_ON = auto()
    INVALID_MOVE_OUT_OF_BOUNDS = auto()
    INVALID_MOVE_NO_DOOR = auto()
    INVALID_MOVE_ACROSS_AREAS = auto()
    INVALID_MOVE_FLEE_TO_UNKNOWN_TILE = auto()
    INVALID_MOVE_ZOMBIE_DOOR_TO_KNOWN_TILE = auto()
    INVALID_VALUE_DIRECTION = auto()
    INVALID_VALUE_MAP_DIMENSION = auto()
    INVALID_VALUE_STARTING_POSITION = auto()
    INVALID_TYPE_MAP_DIMENSION = auto()
    INVALID_TYPE_STARTING_POSITION = auto()
    INVALID_TYPE_RANDOMIZER_SEED = auto()
    FATAL_UNPLACEABLE_TILE = auto()

    """GAME ERRORS"""
    CANT_MOVE_NOW = auto()
    CANT_ROTATE_NOW = auto()
    CANT_PLACE_NOW = auto()
    NOT_ZOMBIE_DOOR = auto()
    NO_OIL = auto()
    NO_INSTANT_KILL = auto()
    CANT_ATTACK = auto()
    CANT_FLEE = auto()
    HAVENT_FOUND_ITEM = auto()
    CANT_END_TURN_NOW = auto()
    CANT_SEARCH_NOW = auto()
    NOT_WON_OR_LOST = auto()

    """GAME STATE ERRORS"""
    ALREADY_COWERED = auto()

    """ITEM ERRORS"""
    SLOT_EMPTY = auto()
    NO_GASOLINE = auto()
    NO_CHAINSAW = auto()
    NO_SODA = auto()
    NO_SPACE = auto()
    NO_FOUND_ITEM = auto()

    """GENERAL ERRORS"""
    FATAL_ERROR = auto()

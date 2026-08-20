from dataclasses import dataclass

from zimp.domain.common.direction import Direction


@dataclass(frozen=True)
class TileData:
    """TileData class used to hold essential information about individual tiles."""
    id: int
    position: tuple[int, int]
    rotation: Direction
    zombie_door: Direction | None
    is_locked: bool

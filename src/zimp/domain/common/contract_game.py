from typing import Protocol
from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.item_code import ItemCode
from zimp.domain.common.result import Result


class GameContract(Protocol):
    def reset(self) -> None:
        """Reset all game components"""
    def move_player(self, direction: Direction) -> ErrorCode | None:
        """Attempt to move the player in a given direction"""
    def rotate_tile(self) -> ErrorCode | None:
        """Rotate the drawn tile in a given direction"""
    def place_tile(self) -> ErrorCode | None:
        """Attempt to place the drawn tile"""
    def pick_zombie_door(self, direction: Direction) -> ErrorCode | None:
        """Trigger a zombie door attack in the selected direction"""
    def attack(self, use_chainsaw: bool = False, instant_kill: bool = False) -> ErrorCode | None:
        """Fight any zombies on the current tile"""
    def flee(self, direction: Direction, with_oil: bool = False) -> ErrorCode | None:
        """Flee to a previously explored tile"""
    def perform_search_for_item(self) -> ErrorCode | None:
        """Draw a new card to find an item"""
    def ignore_search_for_item(self) -> ErrorCode | None:
        """Choose not to draw a card to find an item"""
    def take_item(self) -> ErrorCode | None:
        """Add the found item to the items"""
    def dont_take_item(self) -> ErrorCode | None:
        """Abandon the item that was found"""
    def discard_item(self, slot_id: int = -1) -> ErrorCode | None:
        """Discard the chosen item from the items"""
    def use_item(self, item_id: ItemCode) -> ErrorCode | None:
        """Use the chosen item (gasoline or soda)"""
    def end_turn(self, is_cower: bool = False) -> Result:
        """End the current turn, optionally cowering"""
    def check_win_loss(self) -> Result:
        """To be called after each action; determines if the player has won or lost"""
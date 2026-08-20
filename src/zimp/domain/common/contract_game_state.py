from typing import Protocol, runtime_checkable

from zimp.domain.common.dev_card import CardEffect
from zimp.domain.common.tile_effect import TileEffect
from zimp.domain.game_state.mode import Mode

@runtime_checkable
class GameStateContract(Protocol):
    """Contract used by the application layer to request changes to the Game State."""
    def reset(self) -> None:
        """Reset the game game_state for a new game."""
    def get_hp(self) -> int:
        """Return current player HP value"""
    def get_time(self) -> int:
        """Return current game time"""
    def get_can_move(self) -> bool:
        """Return whether the player can currently move"""
    def get_is_moving(self) -> bool:
        """Return whether the player is currently placing a tile"""
    def get_can_attack(self) -> bool:
        """Return whether the player can attack"""
    def get_can_flee(self) -> bool:
        """Return whether the player can flee"""
    def get_is_zombie_door(self) -> bool:
        """Return if the player needs to place a zombie door"""
    def get_is_searching_item(self) -> bool:
        """Return whether the player needs to decide whether they'll draw an item"""
    def get_has_found_item(self) -> bool:
        """Return whether the player needs to decide if they'll keep a found item"""
    def get_can_end_turn(self) -> bool:
        """Return whether the player can end the turn"""
    def check_is_won(self) -> bool:
        """Update mode if the game is won"""
    def check_is_lost(self) -> bool:
        """Update mode if the game is lost"""
    def get_is_doing_events(self) -> bool:
        """Return whether the game needs to draw a card"""
    def get_has_ended_turn(self) -> bool:
        """Return whether the player has attempted to end the turn"""
    def advance_time(self) -> None:
        """Advance the game time by 1 hour."""
    def start_move(self) -> None:
        """Transition the player to placing a tile"""
    def end_move(self) -> None:
        """Complete placing tile, draw card"""
    def start_zombie_door(self) -> None:
        """Player needs to place a zombie door"""
    def confirm_zombie_door(self) -> None:
        """Player has locked zombie door, fight zombies"""
    def start_searching_item(self) -> None:
        """Player needs to decide if they'll search for an item"""
    def end_searching_item(self) -> None:
        """Player has finished searching for items, can now end turn"""
    def find_item(self) -> None:
        """Player has searched for an item, now decide if they'll keep it"""
    def end_found_item(self) -> None:
        """Player has decide if they'll keep an item, can now end turn"""
    def change_hp(self, amount: int) -> None:
        """Change the player HP by a specified amount."""
    def apply_card_effect(self, effect: CardEffect):
        """Apply a dev card effect"""
    def start_combat(self, num_zombies: int) -> None:
        """spawn zombies and set the player to in combat"""
    def end_combat(self) -> None:
        """Defeat zombies and set the player to not in combat"""
    def attack(self, attack_bonus: int, instant_kill: bool) -> None:
        """Attack zombies the player is currently fighting"""
    def flee(self, with_oil: bool) -> None:
        """Flee from zombies the player is currently fighting"""
    def cower(self) -> Result:
        """Player cowers"""
    def take_totem(self) -> None:
        """Player picks up the totem"""
    def bury_totem(self) -> None:
        """Player buries the totem"""
    def drink_soda(self) -> None:
        """Player heals from drinking soda"""
    def do_end_turn_effect(self, tile_effect: TileEffect) -> None:
        """Player has ended turn, do any tile effects"""
    def start_new_turn(self) -> None:
        """Reset for new turn"""
from typing import Protocol, runtime_checkable

from zimp.domain.common.dev_card import CardEffect
from zimp.domain.common.result import Result
from zimp.domain.common.tile_effect import TileEffect

@runtime_checkable
class GameStateContract(Protocol):
    """Contract used by the application layer to request changes to the Game State."""

    def reset(self) -> None:
        pass
    def get_hp(self) -> int:
        pass
    def get_time(self) -> int:
        pass
    def get_can_move(self) -> bool:
        pass
    def get_is_moving(self) -> bool:
        pass
    def get_can_attack(self) -> bool:
        pass
    def get_can_flee(self) -> bool:
        pass
    def get_is_zombie_door(self) -> bool:
        pass
    def get_is_searching_item(self) -> bool:
        pass
    def get_has_found_item(self) -> bool:
        pass
    def get_can_end_turn(self) -> bool:
        pass
    def check_is_won(self) -> bool:
        pass
    def check_is_lost(self) -> bool:
        pass
    def get_is_doing_events(self) -> bool:
        pass
    def get_has_ended_turn(self) -> bool:
        pass
    def advance_time(self) -> None:
        pass
    def start_move(self) -> None:
        pass
    def end_move(self) -> None:
        pass
    def start_zombie_door(self) -> None:
        pass
    def confirm_zombie_door(self) -> None:
        pass
    def start_searching_item(self) -> None:
        pass
    def end_searching_item(self) -> None:
        pass
    def find_item(self) -> None:
        pass
    def end_found_item(self) -> None:
        pass
    def change_hp(self, amount: int) -> None:
        pass
    def apply_card_effect(self, effect: CardEffect):
        pass
    def start_combat(self, num_zombies: int) -> None:
        pass
    def end_combat(self) -> None:
        pass
    def attack(self, attack_bonus: int, instant_kill: bool) -> None:
        pass
    def flee(self, with_oil: bool) -> None:
        pass
    def cower(self) -> Result:
        pass
    def take_totem(self) -> None:
        pass
    def bury_totem(self) -> None:
        pass
    def drink_soda(self) -> None:
        pass
    def do_end_turn_effect(self, tile_effect: TileEffect) -> None:
        pass
    def start_new_turn(self) -> None:
        pass
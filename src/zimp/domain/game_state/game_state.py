from dataclasses import dataclass

from zimp.domain.common.dev_card import CardEffect, CardEffectType
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.result import Result
from zimp.domain.common.tile_effect import TileEffect
from zimp.domain.game_state.mode import Mode


@dataclass
class GameState:
    _ZOMBIE_DOOR_NUM_ZOMBIES = 3
    _BASE_ATTACK = 1

    _FLEE_DAMAGE = -1
    _COWER_HEAL_AMOUNT = 3
    _TILE_HEAL_AMOUNT = 1
    _SODA_HEAL_AMOUNT = 2

    _START_TIME = 0
    _MAX_TIME = 2

    mode: Mode = Mode.NONE
    health: int = 6
    hour: int = 0

    has_totem: bool = False
    buried_totem: bool = False

    cowered_this_turn: bool = False
    time_ran_out: bool = False

    in_combat: bool = False
    num_zombies: int = 0

    have_ended_turn: bool = False

    def reset(self) -> None:
        self.mode = Mode.NONE
        self.health = 6
        self.hour = self._START_TIME
        self.has_totem = False
        self.buried_totem = False
        self.cowered_this_turn = False
        self.time_ran_out = False

        self.in_combat = False
        self.num_zombies = 0
        self.have_ended_turn = False

    # get data ---------------------------------------

    def get_hp(self) -> int:
        return self.health

    def get_time(self) -> int:
        return self.hour

    # get state
    def get_can_move(self) -> bool:
        return self.mode == Mode.NONE

    def get_is_moving(self) -> bool:
        return self.mode == Mode.MOVE

    def get_can_attack(self) -> bool:
        return self.mode == Mode.COMBAT

    def get_can_flee(self) -> bool:
        return self.mode == Mode.COMBAT

    def get_is_zombie_door(self) -> bool:
        return self.mode == Mode.ZOMBIE_DOOR

    def get_is_searching_item(self) -> bool:
        return self.mode == Mode.ITEM_SEARCH

    def get_has_found_item(self) -> bool:
        return self.mode == Mode.ITEM_FOUND

    def get_can_end_turn(self) -> bool:
        return self.mode == Mode.EVENTS_FINISHED

    def check_is_won(self) -> bool:
        won = self.buried_totem and self.mode == Mode.NONE and self.health > 0 and not self.time_ran_out
        if won:
            self.mode = Mode.WON
        return won

    def check_is_lost(self) -> bool:
        lost = self.health <= 0 or self.time_ran_out
        if lost:
            self.mode = Mode.LOST
        return lost

    def get_is_doing_events(self) -> bool:
        return self.mode == Mode.DEV_CARD

    def get_has_ended_turn(self) -> bool:
        return self.have_ended_turn

    # update state ---------------------------------------

    def advance_time(self) -> None:
        self.hour += 1
        if self.hour > self._MAX_TIME:
            self.time_ran_out = True

    def start_move(self) -> None:
        self.mode = Mode.MOVE

    def end_move(self) -> None:
        self.mode = Mode.DEV_CARD

    def start_zombie_door(self) -> None:
        self.mode = Mode.ZOMBIE_DOOR

    def confirm_zombie_door(self) -> None:
        self.start_combat(self._ZOMBIE_DOOR_NUM_ZOMBIES)

    def start_searching_item(self) -> None:
        self.mode = Mode.ITEM_SEARCH

    def end_searching_item(self) -> None:
        self.mode = Mode.EVENTS_FINISHED

    def find_item(self) -> None:
        self.mode = Mode.ITEM_FOUND

    def end_found_item(self) -> None:
        self.mode = Mode.EVENTS_FINISHED

    def change_hp(self, amount: int) -> None:
        self.health += amount
        if self.health < 0:
            self.health = 0

    # do actions ---------------------------------------

    def apply_card_effect(self, effect: CardEffect):
        if effect.effect_type == CardEffectType.HEALTH:
            self.change_hp(effect.value)
            self.mode = Mode.EVENTS_FINISHED
        elif effect.effect_type == CardEffectType.ZOMBIES:
            self.start_combat(effect.value)
        elif effect.effect_type == CardEffectType.ITEM:
            self.start_searching_item()
        elif effect.effect_type == CardEffectType.NONE:
            self.mode = Mode.EVENTS_FINISHED

    def start_combat(self, num_zombies: int) -> None:
        self.in_combat = True
        self.num_zombies = num_zombies
        self.mode = Mode.COMBAT

    def end_combat(self) -> None:
        self.in_combat = False
        self.num_zombies = 0
        self.mode = Mode.EVENTS_FINISHED

    def attack(self, attack_bonus: int, instant_kill: bool) -> None:
        if not instant_kill:
            damage = self.num_zombies - (self._BASE_ATTACK + attack_bonus)
            damage = max(0, min(4, damage))
            self.change_hp(-damage)

        self.end_combat()

    def flee(self, with_oil: bool) -> None:
        if not with_oil:
            self.change_hp(self._FLEE_DAMAGE)

        self.end_combat()

    def cower(self) -> Result:
        if self.cowered_this_turn or self.mode != Mode.EVENTS_FINISHED:
            return Result.fail(ErrorCode.ALREADY_COWERED)

        self.change_hp(self._COWER_HEAL_AMOUNT)
        self.cowered_this_turn = True
        return Result.success(None)

    def take_totem(self) -> None:
        self.has_totem = True

    def bury_totem(self) -> None:
        if self.has_totem:
            self.buried_totem = True

    def drink_soda(self) -> None:
        self.change_hp(self._SODA_HEAL_AMOUNT)

    def do_end_turn_effect(self, tile_effect: TileEffect) -> None:
        self.have_ended_turn = True

        if tile_effect == TileEffect.HEALTH:
            self.change_hp(self._TILE_HEAL_AMOUNT)
        elif tile_effect == TileEffect.SEARCH:
            self.start_searching_item()
        elif tile_effect == TileEffect.FIND_TOTEM:
            self.mode = Mode.DEV_CARD
            self.take_totem()
        elif tile_effect == TileEffect.BURY_TOTEM:
            self.mode = Mode.DEV_CARD
            self.bury_totem()

    def start_new_turn(self) -> None:
        self.have_ended_turn = False
        self.cowered_this_turn = False
        self.mode = Mode.NONE

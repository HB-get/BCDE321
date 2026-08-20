from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.item_code import ItemCode
from zimp.domain.common.result import Result


class FakeGameState:
    """Fake GameState used to isolate Game from the real domain classes."""

    def __init__(self) -> None:
        self.reset_calls = -1
        self.reset()

    def reset(self) -> None:
        self.hp = 5
        self.time = 0

        self.can_move = True
        self.is_moving = False
        self.is_zombie_door = False
        self.can_attack = True
        self.can_flee = True
        self.is_searching_item = False
        self.has_found_item = False
        self.can_end_turn = True
        self.is_doing_events = False
        self.has_ended_turn = False
        self.has_won = False
        self.has_lost = False

        self.cower_result = Result.success(None)

        self.reset_calls += 1

        self.apply_card_effect_calls = []
        self.advance_time_calls = 0
        self.start_move_calls = 0
        self.end_move_calls = 0
        self.start_zombie_door_calls = 0
        self.confirm_zombie_door_calls = 0
        self.start_searching_item_calls = 0
        self.end_searching_item_calls = 0
        self.find_item_calls = 0
        self.end_found_item_calls = 0
        self.attack_calls = []
        self.flee_calls = []
        self.cower_calls = 0
        self.drink_soda_calls = 0
        self.do_end_turn_effect_calls = []
        self.start_new_turn_calls = 0

    def get_hp(self) -> int:
        return self.hp

    def get_time(self) -> int:
        return self.time

    def get_can_move(self) -> bool:
        return self.can_move

    def get_is_moving(self) -> bool:
        return self.is_moving

    def get_can_attack(self) -> bool:
        return self.can_attack

    def get_can_flee(self) -> bool:
        return self.can_flee

    def get_is_zombie_door(self) -> bool:
        return self.is_zombie_door

    def get_is_searching_item(self) -> bool:
        return self.is_searching_item

    def get_has_found_item(self) -> bool:
        return self.has_found_item

    def get_can_end_turn(self) -> bool:
        return self.can_end_turn

    def check_is_won(self) -> bool:
        return self.has_won

    def check_is_lost(self) -> bool:
        return self.has_lost

    def get_is_doing_events(self) -> bool:
        return self.is_doing_events

    def get_has_ended_turn(self) -> bool:
        return self.has_ended_turn

    def advance_time(self) -> None:
        self.advance_time_calls += 1
        self.time += 1

    def start_move(self) -> None:
        self.start_move_calls += 1
        self.is_moving = True

    def end_move(self) -> None:
        self.end_move_calls += 1
        self.is_moving = False

    def start_zombie_door(self) -> None:
        self.start_zombie_door_calls += 1
        self.is_zombie_door = True

    def confirm_zombie_door(self) -> None:
        self.confirm_zombie_door_calls += 1
        self.is_zombie_door = False

    def start_searching_item(self) -> None:
        self.start_searching_item_calls += 1
        self.is_searching_item = True

    def end_searching_item(self) -> None:
        self.end_searching_item_calls += 1
        self.is_searching_item = False

    def find_item(self) -> None:
        self.find_item_calls += 1
        self.has_found_item = True

    def end_found_item(self) -> None:
        self.end_found_item_calls += 1
        self.has_found_item = False

    def change_hp(self, amount: int) -> None:
        pass

    def apply_card_effect(self, effect) -> None:
        self.apply_card_effect_calls.append(effect)

    def start_combat(self, num_zombies: int) -> None:
        pass
    def end_combat(self) -> None:
        pass

    def attack(self, attack_bonus: int, instant_kill: bool) -> None:
        self.attack_calls.append((attack_bonus, instant_kill))

    def flee(self, with_oil: bool) -> None:
        self.flee_calls.append(with_oil)

    def cower(self) -> Result:
        self.cower_calls += 1
        return self.cower_result

    def take_totem(self) -> None:
        pass
    def bury_totem(self) -> None:
        pass

    def drink_soda(self) -> None:
        self.drink_soda_calls += 1

    def do_end_turn_effect(self, tile_effect) -> None:
        self.do_end_turn_effect_calls.append(tile_effect)

    def start_new_turn(self) -> None:
        self.start_new_turn_calls += 1


class FakeMovement:
    """Fake Movement used to isolate Game from the map/movement domain."""

    def __init__(self) -> None:
        self.reset_calls = -1
        self.reset()

    def reset(self, map_dimensions=None, starting_position=None,
              randomizer_seed=None) -> ErrorCode | None:

        self.reset_calls += 1

        self.move_result = None
        self.flee_result = None
        self.create_zombie_door_result = None
        self.rotate_placement_tile_result = None
        self.lock_placement_tile_result = None
        self.tile_effect = None
        self.placement_mode_on = False
        self.needs_zombie_door = False

        self.move_calls = []
        self.flee_calls = []
        self.create_zombie_door_calls = []
        self.rotate_placement_tile_calls = 0
        self.lock_placement_tile_calls = 0
        self.need_zombie_door_calls = 0
        self.is_placement_mode_on_calls = 0
        self.get_tile_effect_calls = 0

        self.reset_randomizer_seed = randomizer_seed
        self.reset_map_dimensions = map_dimensions
        self.reset_starting_position = starting_position

        return None

    def move(self, direction: Direction) -> ErrorCode | None:
        self.move_calls.append(direction)
        return self.move_result

    def flee(self, direction: Direction) -> ErrorCode | None:
        self.flee_calls.append(direction)
        return self.flee_result

    def create_zombie_door(
        self,
        direction: Direction
    ) -> ErrorCode | None:
        self.create_zombie_door_calls.append(direction)
        return self.create_zombie_door_result

    def rotate_placement_tile(self) -> ErrorCode | None:
        self.rotate_placement_tile_calls += 1
        return self.rotate_placement_tile_result

    def lock_placement_tile(self) -> ErrorCode | None:
        self.lock_placement_tile_calls += 1
        return self.lock_placement_tile_result

    def need_zombie_door(self) -> bool:
        self.need_zombie_door_calls += 1
        return self.needs_zombie_door

    def is_placement_mode_on(self) -> bool:
        self.is_placement_mode_on_calls += 1
        return self.placement_mode_on

    def get_tile_effect(self):
        self.get_tile_effect_calls += 1
        return self.tile_effect

    def get_tile_data(self):
        return []

    def get_player_position(self):
        return 0, 0

    def get_map_dimensions(self):
        return 0, 0


class FakeItems:
    """Fake Items used to isolate Game from inventory behaviour."""

    def __init__(self) -> None:
        self.reset_calls = -1
        self.reset()

    def reset(self) -> None:
        self.reset_calls += 1

        self.attack_bonus_result = Result.success(0)
        self.instant_kill_available = False
        self.has_oil = True
        self.keep_found_item_result = None
        self.discard_result = None
        self.use_result = None
        self.held_items_result = (
            ItemCode.NONE,
            ItemCode.NONE,
        )

        self.attack_bonus_calls = []
        self.record_battle_calls = 0
        self.discard_calls = []
        self.find_item_calls = []
        self.keep_found_item_calls = 0
        self.dont_take_item_calls = 0
        self.use_calls = []
        self.get_has_instant_kill_calls = 0
        self.get_has_oil_calls = 0
        self.held_items_calls = 0

    def record_battle(self) -> None:
        self.record_battle_calls += 1

    def attack_bonus(self, with_chainsaw: bool) -> Result:
        self.attack_bonus_calls.append(with_chainsaw)
        return self.attack_bonus_result

    def held_items(self) -> tuple[ItemCode, ItemCode]:
        self.held_items_calls += 1
        return self.held_items_result

    def get_has_instant_kill(self) -> bool:
        self.get_has_instant_kill_calls += 1
        return self.instant_kill_available

    def get_has_oil(self) -> bool:
        self.get_has_oil_calls += 1
        return self.has_oil

    def find_item(self, item_id: ItemCode) -> None:
        self.find_item_calls.append(item_id)

    def keep_found_item(self) -> ErrorCode | None:
        self.keep_found_item_calls += 1
        return self.keep_found_item_result

    def dont_take_item(self) -> None:
        self.dont_take_item_calls += 1

    def discard(self, slot_id: int) -> ErrorCode | None:
        self.discard_calls.append(slot_id)
        return self.discard_result

    def use(self, item_id: ItemCode) -> ErrorCode | None:
        self.use_calls.append(item_id)
        return self.use_result


class FakeEvents:
    """Fake Events used to isolate Game from the event/card system."""

    def __init__(self) -> None:
        self.reset_calls = -1
        self.reset()

    def reset(self) -> None:
        self.reset_calls += 1

        self.draw_event_result = Result.success("event")
        self.draw_event_shuffled = False

        self.draw_item_result = Result.success(ItemCode.SODA)
        self.draw_item_shuffled = False

        self.waste_time_result = Result.success(None)
        self.waste_time_shuffled = False

        self.draw_event_calls = []
        self.draw_item_calls = 0
        self.waste_time_calls = 0

    def get_remaining_card_count(self):
        return 0
    def draw_event(self, time: int) -> tuple[Result, bool]:
        self.draw_event_calls.append(time)
        return self.draw_event_result, self.draw_event_shuffled

    def draw_item(self) -> tuple[Result, bool]:
        self.draw_item_calls += 1
        return self.draw_item_result, self.draw_item_shuffled

    def waste_time(self) -> tuple[Result, bool]:
        self.waste_time_calls += 1
        return self.waste_time_result, self.waste_time_shuffled
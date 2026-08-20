import pytest

from zimp.domain.common.dev_card import DevCard, CardEffect, CardEffectType
from zimp.domain.common.direction import Direction
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.item_code import ItemCode
from zimp.domain.game.game import Game

from zimp.domain.state.game_state import GameState
from zimp.domain.events.events import Events
from zimp.domain.items.game_items import GameItems
from zimp.domain.movement.game_map import GameMap

# ---------------------------------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------------------------------

@pytest.fixture
def combat_components():
    state = GameState()
    movement = GameMap()
    items = GameItems()
    events = Events((DevCard(
        (
            CardEffect(CardEffectType.ZOMBIES, 5),
            CardEffect(CardEffectType.ZOMBIES, 5),
            CardEffect(CardEffectType.ZOMBIES, 5),
        ),
        ItemCode.NONE,
    ),)*9)

    game = Game(state, movement, items, events, map_seed=3) # foyer -> family room

    return game, state, movement, items, events

@pytest.fixture
def item_components():
    state = GameState()
    movement = GameMap()
    items = GameItems()
    events = Events((DevCard(
        (
            CardEffect(CardEffectType.ITEM),
            CardEffect(CardEffectType.ITEM),
            CardEffect(CardEffectType.ITEM),
        ),
        ItemCode.MACHETE,
        ),)*9)

    game = Game(state, movement, items, events, map_seed=3) # foyer -> family room

    return game, state, movement, items, events

@pytest.fixture
def none_components():
    state = GameState()
    movement = GameMap()
    items = GameItems()
    events = Events((DevCard(
        (
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.NONE),
        ),
        ItemCode.NONE,
        ),)*9)

    game = Game(state, movement, items, events, map_seed=3) # foyer -> family room

    return game, state, movement, items, events

# ---------------------------------------------------------------------------------------------------
# New regression tests
# ---------------------------------------------------------------------------------------------------

# Found a bug? Figure out how to reproduce it and add a test checking it does not occur here

def test_items_gracefully_handles_having_invalid_item_added(none_components):
    game, _, _, items, _ = none_components

    items.find_item(ItemCode.NONE)
    items.keep_found_item()


# ---------------------------------------------------------------------------------------------------
# Base tests
# ---------------------------------------------------------------------------------------------------

# Reset ------------------------------------------------------------------------------------------------
def test_reset_resets_all_components(none_components):
    game, state, movement, items,events = none_components

    #state modification
    start_hp = state.get_hp()
    state.change_hp(1)

    #movement modification
    assert movement.move(Direction.NORTH) is None
    
    #items modification
    items.find_item(ItemCode.CANDLE)
    items.keep_found_item()
    
    #events modification
    start_cards = events.get_remaining_card_count()
    events.waste_time()

    game.reset()

    # Check initial values
    assert state.get_hp() == start_hp
    assert movement.is_placement_mode_on() is False
    assert items.held_items() ==(ItemCode.NONE, ItemCode.NONE)
    assert events.get_remaining_card_count() == start_cards

# move_player ------------------------------------------------------------------------------------------------
def test_north_move_is_allowed_at_start(none_components):
    game, _, _, _,_ = none_components

    result = game.move_player(Direction.NORTH)

    assert not isinstance(result, ErrorCode)

def test_move_success_doesnt_allow_another_move(none_components):
    game, _, _, _,_ = none_components
    game.move_player(Direction.NORTH)

    result = game.move_player(Direction.SOUTH)

    assert result == ErrorCode.CANT_MOVE_NOW

def test_can_only_move_north_at_start(none_components):
    game, _, _, _,_ = none_components

    result = game.move_player(Direction.WEST)

    assert result == ErrorCode.INVALID_MOVE_NO_DOOR

    result = game.move_player(Direction.NORTH)

    assert result is None

def test_cant_move_after_placing_tile(none_components):
    game, _, movement, _,_ = none_components

    game.move_player(Direction.NORTH)
    game.place_tile()

    result = game.move_player(Direction.SOUTH)
    assert result == ErrorCode.CANT_MOVE_NOW

# rotate_tile ------------------------------------------------------------------------------------------------
def test_can_rotate_after_move(none_components):
    game, _, movement, _,_ = none_components

    result = game.move_player(Direction.NORTH)

    assert result is None

    result = game.rotate_tile()

    assert result is None

def test_rotate_tile_only_allowed_after_move(none_components):
    game, _, movement, _,_ = none_components

    result1 = game.rotate_tile()
    assert result1 == ErrorCode.CANT_ROTATE_NOW

    game.move_player(Direction.NORTH)
    result2 = game.rotate_tile()

    assert result2 is None

def test_move_failure_doesnt_allow_rotate(none_components):
    game, _, movement, _,_ = none_components

    assert game.move_player(Direction.SOUTH) is not None

    result = game.rotate_tile()
    assert result == ErrorCode.CANT_ROTATE_NOW

#place_tile ------------------------------------------------------------------------------------------------
def test_place_tile_works_after_move(none_components):
    game, _, _, _,_ = none_components

    game.move_player(Direction.NORTH)
    result = game.place_tile()

    assert result is None

def test_cant_place_tile_if_havent_moved(none_components):
    game, _, movement, _,_ = none_components

    result = game.place_tile()

    assert result == ErrorCode.CANT_PLACE_NOW

def test_place_tile_cant_be_unaligned(none_components):
    _, state, movement, items,events = none_components
    for i in range(4):
        game = Game(state, movement, items, events, map_seed=5) # foyer -> bathroom

        game.move_player(Direction.NORTH)

        for _ in range(i):
            game.rotate_tile()

        result = game.place_tile()
        assert result is None

def test_returning_to_known_tile_doesnt_require_place(none_components):
    game, _, _, _, _ = none_components
    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None
    assert game.end_turn() is None

    assert game.move_player(Direction.SOUTH) is None

    result1 = game.place_tile()

    assert result1 is ErrorCode.CANT_PLACE_NOW

    result2 = game.end_turn()

    assert result2 is None


# Zombie door ------------------------------------------------------------------------------------------------
def test_zombie_door_pick_works_when_needed_after_none_event(none_components):
    _, state, movement, items, events = none_components
    game = Game(state, movement, items, events, map_seed=5) # foyer -> bathroom

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    assert movement.need_zombie_door() is True

    result = game.pick_zombie_door(Direction.NORTH)

    assert result is None

def test_zombie_door_pick_works_when_needed_after_zombies_event(combat_components):
    _, state, movement, items, events = combat_components
    game = Game(state, movement, items, events, map_seed=5) # foyer -> bathroom

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None
    assert game.attack() is None

    assert movement.need_zombie_door() is True

    result = game.pick_zombie_door(Direction.NORTH)

    assert result is None

def test_zombie_door_pick_works_when_needed_after_item_event(item_components):
    _, state, movement, items, events = item_components
    game = Game(state, movement, items, events, map_seed=5)  # foyer -> bathroom

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None
    assert game.ignore_search_for_item() is None

    assert movement.need_zombie_door() is True

    result = game.pick_zombie_door(Direction.NORTH)

    assert result is None

def test_zombie_door_pick_works_when_needed_after_health_event(none_components):
    _, state, movement, items,_ = none_components
    events = Events((DevCard(
            (
                CardEffect(CardEffectType.HEALTH, 1),
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.NONE),
            ),
            ItemCode.NONE,
        ),)*4)
    game = Game(state, movement, items, events, map_seed=5) # foyer -> bathroom

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    assert movement.need_zombie_door() is True

    result = game.pick_zombie_door(Direction.NORTH)

    assert result is None

def test_zombie_door_pick_without_need_fails(none_components):
    game, _, _, _, _ = none_components

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result = game.pick_zombie_door(Direction.NORTH)

    assert result is ErrorCode.NOT_ZOMBIE_DOOR

#attack ------------------------------------------------------------------------------------------------
def test_attack_in_combat_works(combat_components):
    game, state, movement, items, events = combat_components

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result = game.attack()

    assert result is None


def test_attack_with_machete_calculates_damage_correctly(combat_components):
    game, state, movement, items, events = combat_components
    start_hp = state.get_hp()

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None
    items.find_item(ItemCode.MACHETE)
    assert items.keep_found_item() is None

    result = game.attack()

    assert result is None
    assert state.get_hp() == start_hp - 2

def test_attack_during_move_fails(none_components):
    game, _, _, _,_ = none_components

    assert game.move_player(Direction.NORTH) is None

    result = game.attack()

    assert result == ErrorCode.CANT_ATTACK

def test_attack_during_item_search_fails(item_components):
    game, _, _, _, _ = item_components

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result = game.attack()

    assert result == ErrorCode.CANT_ATTACK

def test_attack_with_chainsaw_and_fuel_works(combat_components):
    game, state, movement, items, events = combat_components

    items.find_item(ItemCode.CHAINSAW)
    assert items.keep_found_item() is None
    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result = game.attack(use_chainsaw=True)

    assert result is None

def test_attack_with_chainsaw_without_fuel_fails(combat_components):
    game, state, movement, items, events = combat_components

    items.find_item(ItemCode.CHAINSAW)
    assert items.keep_found_item() is None
    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    items.record_battle()
    items.record_battle()
    result = game.attack(use_chainsaw=True)

    assert result is ErrorCode.NO_CHAINSAW

def test_attack_with_chainsaw_without_chainsaw_fails(combat_components):
    game, state, movement, items, events = combat_components

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result = game.attack(use_chainsaw=True)

    assert result is ErrorCode.NO_CHAINSAW

def test_attack_with_instant_kill_does_no_damage(combat_components):
    game, state, movement, items, events = combat_components

    items.find_item(ItemCode.CANDLE)
    assert items.keep_found_item() is None
    items.find_item(ItemCode.OIL)
    assert items.keep_found_item() is None
    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result = game.attack(instant_kill=True)

    assert result is None

def test_attack_with_instant_kill_without_items_fails(combat_components):
    game, state, movement, items, events = combat_components

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result = game.attack(instant_kill=True)

    assert result is ErrorCode.NO_INSTANT_KILL

#flee ------------------------------------------------------------------------------------------------
def test_flee_from_combat_works(combat_components):
    game, state, movement, items, events = combat_components

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result = game.flee(Direction.SOUTH)

    assert result is None

def test_flee_to_unexplored_tile_fails(combat_components):
    game, state, movement, items, events = combat_components

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result1 = game.flee(Direction.WEST)
    result2 = game.flee(Direction.NORTH)
    result3 = game.flee(Direction.EAST)

    assert result1 == ErrorCode.INVALID_MOVE_FLEE_TO_UNKNOWN_TILE
    assert result2 == ErrorCode.INVALID_MOVE_FLEE_TO_UNKNOWN_TILE
    assert result3 == ErrorCode.INVALID_MOVE_FLEE_TO_UNKNOWN_TILE

def test_flee_without_oil_does_damage(combat_components):
    game, state, movement, items, events = combat_components
    start_hp = state.get_hp()

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result = game.flee(Direction.SOUTH)

    assert result is None
    assert state.get_hp() < start_hp


def test_flee_with_oil_does_no_damage(combat_components):
    game, state, movement, items, events = combat_components
    start_hp = state.get_hp()

    items.find_item(ItemCode.OIL)
    assert items.keep_found_item() is None
    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result = game.flee(Direction.SOUTH, with_oil=True)

    assert result is None
    assert state.get_hp() == start_hp

def test_flee_with_oil_without_oil_fails(combat_components):
    game, state, movement, items, events = combat_components

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result = game.flee(Direction.SOUTH, with_oil=True)

    assert result is ErrorCode.NO_OIL

def test_flee_during_item_search_fails(item_components):
    game, _, _, _, _ = item_components

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result = game.flee(Direction.SOUTH)

    assert result == ErrorCode.CANT_FLEE

def test_flee_during_move_fails(none_components):
    game, _, _, _,_ = none_components

    assert game.move_player(Direction.NORTH) is None

    result = game.flee(Direction.SOUTH)

    assert result == ErrorCode.CANT_FLEE

#end_turn ------------------------------------------------------------------------------------------------
def test_end_turn_with_health_tile_effect_heals(combat_components):
    _, state, movement, items, events = combat_components
    game = Game(state, movement, items, events, map_seed=7) # foyer -> kitchen

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None
    assert game.attack() is None
    start_hp = state.get_hp()

    game.end_turn()

    assert state.get_hp() == start_hp + 1

def test_end_turn_with_cower_restores_health(none_components):
    game, state, _, _, _ = none_components
    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None
    start_hp = state.get_hp()

    game.end_turn(is_cower=True)

    assert state.get_hp() == start_hp + 3

def test_end_turn_with_item_tile_effect_lets_item_search(none_components):
    _, state, movement, items, events = none_components
    game = Game(state, movement, items, events, map_seed=10) #foyer -> family room -> storage

    for _ in range(2):
        assert game.move_player(Direction.NORTH) is None
        assert game.place_tile() is None
        assert game.end_turn() is None

    print(state.mode)

    assert game.perform_search_for_item() is None

def test_end_turn_with_find_totem_draws_card_and_doesnt_win(none_components):
    _, state, movement, items, events = none_components
    game = Game(state, movement, items, events, map_seed=2) # foyer -> evil temple
    print("#####")
    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None
    start_cards = events.get_remaining_card_count()

    game.end_turn()
    assert events.get_remaining_card_count() == start_cards - 1
    assert game.move_player(Direction.NORTH) is None

    assert game.check_win_loss().is_fail()


def test_end_turn_with_bury_totem_without_totem_fails(none_components):
    _, state, movement, items,_ = none_components
    events = Events((DevCard(
        (
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.NONE),
        ),
        ItemCode.NONE,
    ),) * 8)
    game = Game(state, movement, items, events, map_seed=18) # foyer -> family room -> patio -> graveyard

    for _ in range(3):
        assert game.move_player(Direction.NORTH) is None
        assert game.place_tile() is None
        assert game.end_turn() is None

    assert game.check_win_loss().is_fail()

def test_end_turn_during_move_fails(none_components):
    game, _, _, _,_ = none_components
    game.move_player(Direction.NORTH)

    result = game.end_turn()

    assert result == ErrorCode.CANT_END_TURN_NOW

def test_end_turn_during_combat_fails(combat_components):
    game, state, movement, items, events = combat_components

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result = game.end_turn()
    assert result == ErrorCode.CANT_END_TURN_NOW

    assert game.attack() is None

def test_end_turn_during_item_search_fails(item_components):
    game, _, _, _, _ = item_components

    assert game.move_player(Direction.NORTH) is None
    assert game.place_tile() is None

    result = game.end_turn()
    assert result == ErrorCode.CANT_END_TURN_NOW

    assert game.ignore_search_for_item() is None


#perform_search_for_item ------------------------------------------------------------------------------------------------
def test_search_for_item_doesnt_fail(item_components):
    game, _, _, items, _ = item_components
    game.move_player(Direction.NORTH)
    game.place_tile()

    assert game.perform_search_for_item() is None

def test_search_for_item_during_move_fails(item_components):
    game, _, _, _, _ = item_components
    game.move_player(Direction.NORTH)

    result = game.perform_search_for_item()

    assert result == ErrorCode.CANT_SEARCH_NOW

#ignore_search_for_item ------------------------------------------------------------------------------------------------
def test_ignore_search_during_search_doesnt_fail(item_components):
    game, state, _, items, _ = item_components
    game.move_player(Direction.NORTH)
    game.place_tile()

    assert game.ignore_search_for_item() is None

def test_ignore_search_not_during_move_fails(item_components):
    game, _, _, _, _ = item_components
    game.move_player(Direction.NORTH)

    result = game.ignore_search_for_item()

    assert result == ErrorCode.CANT_SEARCH_NOW

#take_item ------------------------------------------------------------------------------------------------
def test_take_item_with_found_gives_that_item(item_components):
    game, _, _, items, _ = item_components
    game.move_player(Direction.NORTH)
    game.place_tile()

    assert game.perform_search_for_item() is None
    game.take_item()

    assert ItemCode.MACHETE in items.held_items()

def test_take_item_during_move_fails(item_components):
    game, _, _, _, _ = item_components
    game.move_player(Direction.NORTH)

    result = game.take_item()
    assert result == ErrorCode.HAVENT_FOUND_ITEM

def test_take_item_with_full_inventory_fails(item_components):
    game, _, _, items, _ = item_components
    game.move_player(Direction.NORTH)

    items.find_item(ItemCode.MACHETE)
    items.keep_found_item()
    items.find_item(ItemCode.OIL)
    items.keep_found_item()

    game.place_tile()

    game.perform_search_for_item()
    result = game.take_item()

    assert result == ErrorCode.NO_SPACE

#dont_take_item ------------------------------------------------------------------------------------------------
def test_dont_take_item_works(item_components):
    game, _, _, items, _ = item_components
    game.move_player(Direction.NORTH)
    game.place_tile()

    assert game.ignore_search_for_item() is None

    assert items.held_items() == (ItemCode.NONE, ItemCode.NONE)

def test_dont_take_item_during_move_fails(item_components):
    game, _, _, _, _ = item_components
    game.move_player(Direction.NORTH)

    result = game.take_item()
    assert result == ErrorCode.HAVENT_FOUND_ITEM
def test_dont_take_item_with_full_inventory_doesnt_fail(item_components):
    game, _, _, items, _ = item_components
    game.move_player(Direction.NORTH)

    items.find_item(ItemCode.MACHETE)
    items.keep_found_item()
    items.find_item(ItemCode.OIL)
    items.keep_found_item()

    game.place_tile()

    game.perform_search_for_item()
    result = game.dont_take_item()

    assert result is None


#discard_item ------------------------------------------------------------------------------------------------
def test_discard_item_with_item_works(none_components):
    game, _, _, items,_ = none_components
    items.find_item(ItemCode.GASOLINE)
    items.keep_found_item()

    result = items.discard(0)

    assert result is None

def test_discard_item_with_no_item_fails(none_components):
    game, _, _, items,_ = none_components

    result = items.discard(0)

    assert result == ErrorCode.SLOT_EMPTY

#use_item ------------------------------------------------------------------------------------------------
def test_use_gasoline_with_gasoline_and_chainsaw_refuels(combat_components):
    game, _, _, items, _ = combat_components
    items.find_item(ItemCode.CHAINSAW)
    items.keep_found_item()
    items.find_item(ItemCode.GASOLINE)
    items.keep_found_item()

    items.record_battle()
    items.record_battle()
    game.move_player(Direction.NORTH)
    game.place_tile()

    assert game.attack(use_chainsaw=True) == ErrorCode.NO_CHAINSAW
    assert game.use_item(ItemCode.GASOLINE) is None

    result = game.attack(use_chainsaw=True)

    assert result is None

def test_use_soda_heals(none_components):
    game, state, _, items,_ = none_components
    items.find_item(ItemCode.SODA)
    items.keep_found_item()
    start_hp = state.get_hp()

    result = game.use_item(ItemCode.SODA)

    assert result is None
    assert state.get_hp() == start_hp + 2

def test_use_other_items_fails(none_components):
    _, state, movement, _,events = none_components
    for item in (ItemCode.CHAINSAW, ItemCode.MACHETE, ItemCode.CANDLE,
                 ItemCode.GOLF_CLUB, ItemCode.GRISLY_FEMUR, ItemCode.BOARD_WITH_NAILS, ItemCode.OIL):
        items = GameItems()
        game = Game(state, movement, items, events)

        items.find_item(item)
        items.keep_found_item()

        result = game.use_item(item)

        assert isinstance(result, ErrorCode)

def test_use_gasoline_without_gasoline_fails(none_components):
    game, _, _, items,_ = none_components
    items.find_item(ItemCode.CHAINSAW)
    items.keep_found_item()

    result = game.use_item(ItemCode.GASOLINE)

    assert result == ErrorCode.NO_GASOLINE

def test_use_gasoline_without_chainsaw_fails(none_components):
    game, _, _, items,_ = none_components
    items.find_item(ItemCode.GASOLINE)
    items.keep_found_item()

    result = game.use_item(ItemCode.GASOLINE)

    assert result == ErrorCode.NO_CHAINSAW

def test_use_soda_without_soda_fails(none_components):
    game, state, _, _,_ = none_components
    start_hp = state.get_hp()

    result = game.use_item(ItemCode.SODA)

    assert result == ErrorCode.NO_SODA
    assert state.get_hp() == start_hp

#check_win_loss ------------------------------------------------------------------------------------------------

def test_exhaust_hp_loses(combat_components):
    game, _, movement, _, _ = combat_components

    for _ in range(2):
        print(game.move_player(Direction.NORTH))
        print(game.place_tile())
        print(game.attack())
        print(game.end_turn())
        print(game._state.get_hp())

    result = game.check_win_loss()

    assert result.get_data() == "You lose!"

def test_out_of_time_loses(none_components):
    _, state, movement, items,_ = none_components
    events = Events((DevCard(
        (
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.NONE),
        ),
        ItemCode.NONE,
    ),) * 3)
    game = Game(state, movement, items, events)

    for _ in range(20):
        result, shuffled = events.waste_time()
        if shuffled:
            state.advance_time()

    result = game.check_win_loss()

    assert result.get_data() == "You lose!"

def test_not_buried_hp_left_not_out_of_time_does_nothing(none_components):
    game, _, _, _,_ = none_components

    game.move_player(Direction.NORTH)
    game.place_tile()
    game.end_turn()

    result = game.check_win_loss()

    assert result.is_fail()

def test_end_turn_with_bury_totem_with_totem_draws_card_and_wins(none_components):
    _, state, movement, items,_ = none_components
    events = Events((DevCard(
        (
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.NONE),
        ),
        ItemCode.NONE,
    ),)*8)
    game = Game(state, movement, items, events, map_seed=408) #foyer -> evil temple -> family room -> patio -> graveyard

    for _ in range(4):
        assert game.move_player(Direction.NORTH) is None
        assert game.place_tile() is None
        assert game.end_turn() is None

    assert game.check_win_loss().get_data() == "You win!"
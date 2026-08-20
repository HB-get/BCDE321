import pytest

from zimp.domain.common.dev_card import DevCard, CardEffect, CardEffectType
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.item_code import ItemCode
from zimp.domain.events.events import Events


# -----------------------------------------------------------------------------------------------------------
# Setup fixtures
# -----------------------------------------------------------------------------------------------------------

@pytest.fixture
def sample_cards():
    return (
        DevCard(
            (
                CardEffect(CardEffectType.NONE),
                CardEffect(CardEffectType.ITEM),
                CardEffect(CardEffectType.ZOMBIES, 6),
            ),
            ItemCode.NONE,
        ),
        DevCard(
            (
                CardEffect(CardEffectType.ZOMBIES, 4),
                CardEffect(CardEffectType.HEALTH, -1),
                CardEffect(CardEffectType.ITEM),
            ),
            ItemCode.OIL,
        ),
        DevCard(
            (
                CardEffect(CardEffectType.ITEM),
                CardEffect(CardEffectType.ZOMBIES, 4),
                CardEffect(CardEffectType.HEALTH, -1),
            ),
            ItemCode.GASOLINE,
        ),
    )


@pytest.fixture
def deck(sample_cards):
    """A fresh Events instance for each test."""
    return Events(sample_cards)


# -----------------------------------------------------------------------------------------------------------
# Constructor / validation
# -----------------------------------------------------------------------------------------------------------

def test_none_cards_raises_value_error():
    with pytest.raises(ValueError, match="No dev cards configured"):
        Events(None)  # type: ignore[arg-type]

def test_empty_cards_raises_value_error():
    with pytest.raises(ValueError, match="No dev cards configured"):
        Events(())

def test_less_than_three_cards_raises_runtime_error():
    card = DevCard(
        (
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.NONE),
        ),
        ItemCode.NONE,
    )

    with pytest.raises(
        ValueError,
        match="Dev card deck must have at least 3 cards",
    ):
        Events((card,))

def test_non_dev_card_raises_value_error():
    with pytest.raises(TypeError, match="Misconfigured dev card"):
        Events((object(), object(), object()))  # type: ignore[arg-type]

def test_non_item_code_raises_type_error():
    card = DevCard(
        (
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.NONE),
        ),
        0,  # type: ignore[arg-type]
    )

    with pytest.raises(TypeError, match="Misconfigured card item"):
        Events((card, card, card))

def test_none_item_code_raises_value_error():
    card = DevCard(
        (
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.NONE),
        ),
        None,  # type: ignore[arg-type]
    )

    with pytest.raises(TypeError, match="Misconfigured card item"):
        Events((card, card, card))

def test_wrong_effect_count_raises_value_error():
    card = DevCard(
        (# type: ignore[arg-type]
            CardEffect(CardEffectType.NONE),
        ),
        ItemCode.NONE,
    )

    with pytest.raises(ValueError, match="Dev cards must have 3 effects"):
        Events((card, card, card))

def test_non_card_effect_in_effects_raises_value_error():
    card = DevCard(
        (# type: ignore[arg-type]
            CardEffect(CardEffectType.NONE),
            "bad",
            CardEffect(CardEffectType.NONE),
        ),
        ItemCode.NONE,
    )

    with pytest.raises(TypeError, match="Misconfigured card effect"):
        Events((card, card, card))

def test_non_card_effect_type_raises_value_error():
    card = DevCard(
        (
            CardEffect(CardEffectType.NONE),
            CardEffect("bad"),  # type: ignore[arg-type]
            CardEffect(CardEffectType.NONE),
        ),
        ItemCode.NONE,
    )

    with pytest.raises(TypeError, match="Misconfigured card effect type"):
        Events((card, card, card))

def test_non_int_effect_value_raises_value_error():
    card = DevCard(
        (
            CardEffect(CardEffectType.NONE),
            CardEffect(CardEffectType.HEALTH, "bad"),  # type: ignore[arg-type]
            CardEffect(CardEffectType.NONE),
        ),
        ItemCode.NONE,
    )

    with pytest.raises(TypeError, match="Misconfigured card effect value"):
        Events((card, card, card))


# -----------------------------------------------------------------------------------------------------------
# Initial state
# -----------------------------------------------------------------------------------------------------------

def test_constructor_creates_object():
    handler = Events()

    assert handler is not None

def test_initial_count_matches_deck(deck, sample_cards):
    assert deck.get_remaining_card_count() == len(sample_cards)

# -----------------------------------------------------------------------------------------------------------
# Reset
# -----------------------------------------------------------------------------------------------------------

def test_reset_discards_two_cards(deck, sample_cards):
    deck.reset()

    assert deck.get_remaining_card_count() == len(sample_cards) - 2

def test_reset_restores_deck_to_full_shuffled_size(deck, sample_cards):
    result, shuffled = deck.draw_item()

    assert not result.is_fail()
    assert shuffled is False
    assert deck.get_remaining_card_count() == len(sample_cards) - 1

    deck.reset()

    assert deck.get_remaining_card_count() == len(sample_cards) - 2

def test_reset_can_be_called_multiple_times(deck, sample_cards):
    deck.reset()
    deck.reset()
    deck.reset()

    assert deck.get_remaining_card_count() == len(sample_cards) - 2

# -----------------------------------------------------------------------------------------------------------
# Remaining card count
# -----------------------------------------------------------------------------------------------------------

def test_no_reset_returns_initial_count(deck, sample_cards):
    assert deck.get_remaining_card_count() == len(sample_cards)

def test_decreases_after_draw_event(deck):
    start = deck.get_remaining_card_count()

    result, shuffled = deck.draw_event(0)

    assert not result.is_fail()
    assert shuffled is False
    assert deck.get_remaining_card_count() == start - 1

def test_decreases_after_draw_item(deck):
    start = deck.get_remaining_card_count()

    result, shuffled = deck.draw_item()

    assert not result.is_fail()
    assert shuffled is False
    assert deck.get_remaining_card_count() == start - 1

def test_decreases_after_waste_time(deck):
    start = deck.get_remaining_card_count()

    result, shuffled = deck.waste_time()

    assert not result.is_fail()
    assert shuffled is False
    assert deck.get_remaining_card_count() == start - 1

def test_can_become_empty(sample_cards):
    handler = Events(sample_cards)

    for _ in range(len(sample_cards)):
        result, shuffled = handler.waste_time()

        assert not result.is_fail()
        assert shuffled is False

    assert handler.get_remaining_card_count() == 0

# -----------------------------------------------------------------------------------------------------------
# Draw event
# -----------------------------------------------------------------------------------------------------------

def test_returns_success_with_effect(deck):
    result, shuffled = deck.draw_event(0)

    assert not result.is_fail()
    assert shuffled is False
    assert isinstance(result.get_data(), CardEffect)

def test_returns_effect_at_requested_time(deck):
    result, shuffled = deck.draw_event(1)

    assert not result.is_fail()
    assert shuffled is False
    assert result.get_data() == CardEffect(CardEffectType.ITEM)

def test_returns_effect_at_last_valid_time(deck):
    result, shuffled = deck.draw_event(2)

    assert not result.is_fail()
    assert shuffled is False
    assert result.get_data() == CardEffect(CardEffectType.ZOMBIES,6)

@pytest.mark.parametrize("time", [-1, 3, 99])
def test_invalid_time_returns_fatal_error(deck, time):
    result, shuffled = deck.draw_event(time)

    assert result.is_fail()
    assert result.get_error_code() == ErrorCode.FATAL_ERROR
    assert shuffled is False

def test_invalid_time_doesnt_consume_card(deck):
    start = deck.get_remaining_card_count()

    result, shuffled = deck.draw_event(-1)

    assert result.is_fail()
    assert shuffled is False
    assert deck.get_remaining_card_count() == start

# -----------------------------------------------------------------------------------------------------------
# Draw item
# -----------------------------------------------------------------------------------------------------------

def test_returns_item_code(deck):
    result, shuffled = deck.draw_item()

    assert not result.is_fail()
    assert shuffled is False
    assert isinstance(result.get_data(), ItemCode)
    assert result.get_data() == ItemCode.NONE

def test_returns_next_card_item_after_draw(deck):
    result, shuffled = deck.draw_item()

    assert not result.is_fail()
    assert shuffled is False
    assert result.get_data() == ItemCode.NONE

    result, shuffled = deck.draw_item()

    assert not result.is_fail()
    assert shuffled is False
    assert result.get_data() == ItemCode.OIL

# -----------------------------------------------------------------------------------------------------------
# Waste time
# -----------------------------------------------------------------------------------------------------------

def test_draws_cards_in_order(sample_cards):
    handler = Events(sample_cards)

    result1, shuffled1 = handler.waste_time()
    result2, shuffled2 = handler.waste_time()
    result3, shuffled3 = handler.waste_time()

    assert shuffled1 is False
    assert shuffled2 is False
    assert shuffled3 is False

    assert result1.get_data() == sample_cards[0]
    assert result2.get_data() == sample_cards[1]
    assert result3.get_data() == sample_cards[2]

    assert handler.get_remaining_card_count() == 0


# -----------------------------------------------------------------------------------------------------------
# Shuffling
# -----------------------------------------------------------------------------------------------------------

def test_drawing_from_empty_deck_shuffles(sample_cards):
    handler = Events(sample_cards)

    for _ in range(len(sample_cards)):
        result, shuffled = handler.waste_time()

        assert not result.is_fail()
        assert shuffled is False

    assert handler.get_remaining_card_count() == 0

    result, shuffled = handler.waste_time()

    assert not result.is_fail()
    assert shuffled is True
    assert isinstance(result.get_data(), DevCard)
    assert handler.get_remaining_card_count() == len(sample_cards) - 3

def test_shuffle_discards_two_cards(sample_cards):
    handler = Events(sample_cards)

    handler.reset()

    assert handler.get_remaining_card_count() == len(sample_cards) - 2

def test_shuffle_flag_only_true_when_shuffle_occurs(sample_cards):
    handler = Events(sample_cards)

    result1, shuffled1 = handler.waste_time()
    result2, shuffled2 = handler.waste_time()
    result3, shuffled3 = handler.waste_time()

    assert not result1.is_fail()
    assert not result2.is_fail()
    assert not result3.is_fail()

    assert shuffled1 is False
    assert shuffled2 is False
    assert shuffled3 is False

    result4, shuffled4 = handler.waste_time()

    assert not result4.is_fail()
    assert shuffled4 is True

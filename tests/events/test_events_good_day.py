import pytest

from zimp.domain.common.dev_card import DevCard, CardEffect, CardEffectType
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.item_code import ItemCode
from zimp.domain.events.events import Events

class TestEventsGoodDay:
    # -----------------------------------------------------------------------------------------------------------
    # Setup fixtures
    # -----------------------------------------------------------------------------------------------------------

    @pytest.fixture
    def sample_cards(self):
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
    def deck(self, sample_cards):
        """A fresh Events instance for each test."""
        return Events(sample_cards)


    # -----------------------------------------------------------------------------------------------------------
    # Constructor / validation
    # -----------------------------------------------------------------------------------------------------------

    def test_constructor_creates_object(self):
        handler = Events()

        assert handler is not None

    def test_initial_count_matches_deck(self, deck, sample_cards):
        assert deck.get_remaining_card_count() == len(sample_cards)

    # -----------------------------------------------------------------------------------------------------------
    # Reset
    # -----------------------------------------------------------------------------------------------------------

    def test_reset_discards_two_cards(self, deck, sample_cards):
        deck.reset()

        assert deck.get_remaining_card_count() == len(sample_cards) - 2

    def test_reset_restores_deck_to_full_shuffled_size(self, deck, sample_cards):
        result, shuffled = deck.draw_item()

        assert not result.is_fail()
        assert shuffled is False
        assert deck.get_remaining_card_count() == len(sample_cards) - 1

        deck.reset()

        assert deck.get_remaining_card_count() == len(sample_cards) - 2

    def test_reset_can_be_called_multiple_times(self, deck, sample_cards):
        deck.reset()
        deck.reset()
        deck.reset()

        assert deck.get_remaining_card_count() == len(sample_cards) - 2

    # -----------------------------------------------------------------------------------------------------------
    # Remaining card count
    # -----------------------------------------------------------------------------------------------------------

    def test_no_reset_returns_initial_count(self, deck, sample_cards):
        assert deck.get_remaining_card_count() == len(sample_cards)

    def test_decreases_after_draw_event(self, deck):
        start = deck.get_remaining_card_count()

        result, shuffled = deck.draw_event(0)

        assert not result.is_fail()
        assert shuffled is False
        assert deck.get_remaining_card_count() == start - 1

    def test_decreases_after_draw_item(self, deck):
        start = deck.get_remaining_card_count()

        result, shuffled = deck.draw_item()

        assert not result.is_fail()
        assert shuffled is False
        assert deck.get_remaining_card_count() == start - 1

    def test_decreases_after_waste_time(self, deck):
        start = deck.get_remaining_card_count()

        result, shuffled = deck.waste_time()

        assert not result.is_fail()
        assert shuffled is False
        assert deck.get_remaining_card_count() == start - 1

    def test_can_become_empty(self, sample_cards):
        handler = Events(sample_cards)

        for _ in range(len(sample_cards)):
            result, shuffled = handler.waste_time()

            assert not result.is_fail()
            assert shuffled is False

        assert handler.get_remaining_card_count() == 0

    # -----------------------------------------------------------------------------------------------------------
    # Draw event
    # -----------------------------------------------------------------------------------------------------------

    def test_returns_success_with_effect(self, deck):
        result, shuffled = deck.draw_event(0)

        assert not result.is_fail()
        assert shuffled is False
        assert isinstance(result.get_data(), CardEffect)

    def test_returns_effect_at_requested_time(self, deck):
        result, shuffled = deck.draw_event(1)

        assert not result.is_fail()
        assert shuffled is False
        assert result.get_data() == CardEffect(CardEffectType.ITEM)

    def test_returns_effect_at_last_valid_time(self, deck):
        result, shuffled = deck.draw_event(2)

        assert not result.is_fail()
        assert shuffled is False
        assert result.get_data() == CardEffect(CardEffectType.ZOMBIES,6)

    # -----------------------------------------------------------------------------------------------------------
    # Draw item
    # -----------------------------------------------------------------------------------------------------------

    def test_returns_item_code(self, deck):
        result, shuffled = deck.draw_item()

        assert not result.is_fail()
        assert shuffled is False
        assert isinstance(result.get_data(), ItemCode)
        assert result.get_data() == ItemCode.NONE

    def test_returns_next_card_item_after_draw(self, deck):
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

    def test_draws_cards_in_order(self, sample_cards):
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

    def test_drawing_from_empty_deck_shuffles(self, sample_cards):
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

    def test_shuffle_discards_two_cards(self, sample_cards):
        handler = Events(sample_cards)

        handler.reset()

        assert handler.get_remaining_card_count() == len(sample_cards) - 2

    def test_shuffle_flag_only_true_when_shuffle_occurs(self, sample_cards):
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

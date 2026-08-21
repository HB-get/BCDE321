import pytest

from zimp.domain.common.dev_card import DevCard, CardEffect, CardEffectType
from zimp.domain.common.error_code import ErrorCode
from zimp.domain.common.item_code import ItemCode
from zimp.domain.events.events import Events

class TestEventsBadDay:
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

    def test_none_cards_raises_value_error(self):
        with pytest.raises(ValueError, match="No dev cards configured"):
            Events(None)  # type: ignore[arg-type]

    def test_empty_cards_raises_value_error(self):
        with pytest.raises(ValueError, match="No dev cards configured"):
            Events(())

    def test_less_than_three_cards_raises_runtime_error(self):
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

    def test_non_dev_card_raises_value_error(self):
        with pytest.raises(TypeError, match="Misconfigured dev card"):
            Events((object(), object(), object()))  # type: ignore[arg-type]

    def test_non_item_code_raises_type_error(self):
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

    def test_none_item_code_raises_value_error(self):
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

    def test_wrong_effect_count_raises_value_error(self):
        card = DevCard(
            (# type: ignore[arg-type]
                CardEffect(CardEffectType.NONE),
            ),
            ItemCode.NONE,
        )

        with pytest.raises(ValueError, match="Dev cards must have 3 effects"):
            Events((card, card, card))

    def test_non_card_effect_in_effects_raises_value_error(self):
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

    def test_non_card_effect_type_raises_value_error(self):
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

    def test_non_int_effect_value_raises_value_error(self):
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
    # Reset
    # -----------------------------------------------------------------------------------------------------------



    # -----------------------------------------------------------------------------------------------------------
    # Remaining card count
    # -----------------------------------------------------------------------------------------------------------


    # -----------------------------------------------------------------------------------------------------------
    # Draw event
    # -----------------------------------------------------------------------------------------------------------

    @pytest.mark.parametrize("time", [-1, 3, 99])
    def test_invalid_time_returns_fatal_error(self, deck, time):
        result, shuffled = deck.draw_event(time)

        assert result.is_fail()
        assert result.get_error_code() == ErrorCode.FATAL_ERROR
        assert shuffled is False

    def test_invalid_time_doesnt_consume_card(self, deck):
        start = deck.get_remaining_card_count()

        result, shuffled = deck.draw_event(-1)

        assert result.is_fail()
        assert shuffled is False
        assert deck.get_remaining_card_count() == start

    # -----------------------------------------------------------------------------------------------------------
    # Draw item
    # -----------------------------------------------------------------------------------------------------------


    # -----------------------------------------------------------------------------------------------------------
    # Waste time
    # -----------------------------------------------------------------------------------------------------------


    # -----------------------------------------------------------------------------------------------------------
    # Shuffling
    # -----------------------------------------------------------------------------------------------------------

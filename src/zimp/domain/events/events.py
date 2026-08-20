import random

from zimp.domain.common.item_code import ItemCode
from zimp.domain.common.result import Result
from zimp.domain.common.error_code import ErrorCode

from zimp.domain.common.dev_card import DevCard, CardEffectType, CardEffect
from zimp.domain.events.card_data import CARD_DATA


class Events:
    """Handles the dev card deck, shuffling, and drawing"""

    _NUM_DISCARD = 2
    _EFFECTS_LENGTH = 3

    def __init__(self, cards: tuple[DevCard, ...] = CARD_DATA) -> None:
        self._validate_cards(cards)

        # Deck
        self._dev_cards = cards
        self._deck: list[DevCard] = list(cards)

    @staticmethod
    def _validate_cards(cards: tuple[DevCard, ...]):
        """Validates the card deck and raises an error if any problems are found"""
        if cards is None or not cards:
            raise ValueError("No dev cards configured")

        if len(cards) <= 2:
            raise ValueError("Dev card deck must have at least 3 cards")

        for card in cards:
            if not isinstance(card, DevCard):
                raise TypeError("Misconfigured dev card")

            if not isinstance(card.item, ItemCode):
                raise TypeError("Misconfigured card item")

            if len(card.effects) != 3:
                raise ValueError("Dev cards must have 3 effects")

            for effect in card.effects:
                if not isinstance(effect, CardEffect):
                    raise TypeError("Misconfigured card effect")

                if not isinstance(effect.effect_type, CardEffectType):
                    raise TypeError("Misconfigured card effect type")

                if not isinstance(effect.value, int):
                    raise TypeError("Misconfigured card effect value")



    def _shuffle(self) -> None:
        """Shuffle the dev card deck and discard two"""
        deck = list(self._dev_cards)
        random.shuffle(deck)
        self._deck = deck[self._NUM_DISCARD:]

    def _draw_card(self) -> tuple[Result, bool]:
        """Draw a dev card from the deck and return it, shuffling if required"""
        shuffled = False

        if not self._deck:
            self._shuffle()
            shuffled = True

        card = self._deck.pop(0)

        return Result.success(card), shuffled

    def reset(self) -> None:
        """Reset the deck"""
        self._shuffle()

    def get_remaining_card_count(self) -> int:
        """Get the number of dev cards currently in the deck"""
        return len(self._deck)

    def draw_event(self, time: int) -> tuple[Result, bool]:
        """Draw a dev card from the deck and return the effect, shuffling if required"""
        if not 0 <= time < self._EFFECTS_LENGTH:
            return Result.fail(ErrorCode.FATAL_ERROR), False

        card, shuffled = self._draw_card()
        if card.is_fail():
            return card, shuffled

        current_effect = card.get_data().effects[time]

        return Result.success(current_effect), shuffled

    def draw_item(self) -> tuple[Result, bool]:
        """Draw a dev card from the deck and return the item, shuffling if required"""
        card, shuffled = self._draw_card()
        if card.is_fail():
            return card, shuffled

        item = card.get_data().item

        return Result.success(item), shuffled

    def waste_time(self) -> tuple[Result, bool]:
        """Discard a card"""
        return self._draw_card()
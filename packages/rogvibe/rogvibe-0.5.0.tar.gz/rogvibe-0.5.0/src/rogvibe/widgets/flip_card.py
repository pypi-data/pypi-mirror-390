"""Flip card game widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Grid
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static


class Card(Static):
    """A single card widget."""

    def __init__(self, value: str, card_id: int) -> None:
        super().__init__()
        self.value = value
        self.card_id = card_id
        self.is_flipped = False
        self.is_matched = False
        self._update_display()

    def _update_display(self) -> None:
        """Update the card display based on its state."""
        if self.is_matched:
            self.remove_class("flipped")
            self.add_class("matched")
            self.update(f"✓ {self.value} ✓")
        elif self.is_flipped:
            self.add_class("flipped")
            self.update(self.value)
        else:
            self.remove_class("flipped")
            self.remove_class("matched")
            # Card back design - simple centered question mark
            self.update("?")

    def flip(self) -> None:
        """Flip the card to show its value."""
        if not self.is_matched:
            self.is_flipped = True
            self._update_display()

    def unflip(self) -> None:
        """Flip the card back to hide its value."""
        if not self.is_matched:
            self.is_flipped = False
            self._update_display()

    def mark_matched(self) -> None:
        """Mark the card as matched."""
        self.is_matched = True
        self.is_flipped = True
        self._update_display()

    async def on_click(self) -> None:
        """Handle card click."""
        if not self.is_matched and not self.is_flipped:
            # Notify parent to handle the flip
            self.post_message(CardClicked(self, self))


class CardClicked(Message):
    """Message sent when a card is clicked."""

    def __init__(self, sender: Widget, card: Card) -> None:
        try:
            super().__init__(sender)  # type: ignore[arg-type]
        except TypeError:
            super().__init__()
        self._origin = sender
        self.card = card

    @property
    def origin(self) -> Widget:
        """Widget that emitted the message."""
        return self._origin


class FlipCardGrid(Grid):
    """A 4x4 grid of flip cards."""

    def __init__(self, participants: list[str]) -> None:
        super().__init__(id="card_grid")
        self.participants = participants
        # Create pairs - each participant appears twice
        self.values = participants + participants
        # Shuffle the values
        import random

        random.shuffle(self.values)
        self.cards: list[Card] = []
        self.flipped_cards: list[Card] = []
        self.matched_count = 0

    def compose(self) -> ComposeResult:
        """Compose the grid of cards."""
        for i, value in enumerate(self.values):
            card = Card(value, i)
            self.cards.append(card)
            yield card

    async def on_card_clicked(self, event: CardClicked) -> None:
        """Handle card clicks."""
        await self.flip_card(event.card)

    async def flip_card(self, card: Card) -> None:
        """Flip a card and check for matches."""
        # If we already have 2 flipped cards that don't match, flip them back immediately
        if len(self.flipped_cards) >= 2:
            # Cancel any pending timer and flip back immediately
            self._unflip_cards()

        card.flip()
        self.flipped_cards.append(card)

        # Check if we have two cards flipped
        if len(self.flipped_cards) == 2:
            card1, card2 = self.flipped_cards
            if card1.value == card2.value:
                # Match found!
                card1.mark_matched()
                card2.mark_matched()
                self.matched_count += 2
                self.flipped_cards = []

                # Post a message if all cards are matched
                if self.matched_count == len(self.cards):
                    from ..models.messages import AllCardsMatched

                    self.post_message(AllCardsMatched(self, card1.value))
                else:
                    # Post a message for pair matched
                    from ..models.messages import PairMatched

                    self.post_message(PairMatched(self, card1.value))
            else:
                # No match - flip back after a delay
                self.set_timer(1.0, lambda: self._unflip_cards())

    def _unflip_cards(self) -> None:
        """Unflip the currently flipped cards."""
        for card in self.flipped_cards:
            card.unflip()
        self.flipped_cards = []

    def reset(self) -> None:
        """Reset the game."""
        import random

        random.shuffle(self.values)
        self.matched_count = 0
        self.flipped_cards = []
        for i, card in enumerate(self.cards):
            card.value = self.values[i]
            card.is_flipped = False
            card.is_matched = False
            card._update_display()

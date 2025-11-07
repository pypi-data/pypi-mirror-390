"""Message classes for widget communication."""

from __future__ import annotations

from textual.message import Message
from textual.widget import Widget


class SpinFinished(Message):
    """Fired when the wheel stops spinning."""

    def __init__(self, sender: Widget, winner: str) -> None:
        try:
            super().__init__(sender)  # type: ignore[arg-type]  # Textual <=0.43 expects the sender argument.
        except TypeError:
            super().__init__()  # Newer Textual versions no longer take sender.
        self._origin = sender
        self.winner = winner

    @property
    def origin(self) -> Widget:
        """Widget that emitted the message."""
        return self._origin


class SpinTick(Message):
    """Fired each time the wheel advances during spinning."""

    def __init__(self, sender: Widget, dice_face: str) -> None:
        try:
            super().__init__(sender)  # type: ignore[arg-type]
        except TypeError:
            super().__init__()
        self._origin = sender
        self.dice_face = dice_face

    @property
    def origin(self) -> Widget:
        """Widget that emitted the message."""
        return self._origin


class SlotReelSpinning(Message):
    """Fired when a reel is spinning."""

    def __init__(self, sender: Widget, reel_index: int, value: str) -> None:
        try:
            super().__init__(sender)  # type: ignore[arg-type]
        except TypeError:
            super().__init__()
        self._origin = sender
        self.reel_index = reel_index
        self.value = value

    @property
    def origin(self) -> Widget:
        """Widget that emitted the message."""
        return self._origin


class SlotReelStopped(Message):
    """Fired when a reel stops spinning."""

    def __init__(self, sender: Widget, reel_index: int, value: str) -> None:
        try:
            super().__init__(sender)  # type: ignore[arg-type]
        except TypeError:
            super().__init__()
        self._origin = sender
        self.reel_index = reel_index
        self.value = value

    @property
    def origin(self) -> Widget:
        """Widget that emitted the message."""
        return self._origin


class SlotAllStopped(Message):
    """Fired when all reels have stopped."""

    def __init__(self, sender: Widget, results: list[str]) -> None:
        try:
            super().__init__(sender)  # type: ignore[arg-type]
        except TypeError:
            super().__init__()
        self._origin = sender
        self.results = results

    @property
    def origin(self) -> Widget:
        """Widget that emitted the message."""
        return self._origin


class AllCardsMatched(Message):
    """Fired when all cards are matched in the flip card game."""

    def __init__(self, sender: Widget, winner: str) -> None:
        try:
            super().__init__(sender)  # type: ignore[arg-type]
        except TypeError:
            super().__init__()
        self._origin = sender
        self.winner = winner

    @property
    def origin(self) -> Widget:
        """Widget that emitted the message."""
        return self._origin


class PairMatched(Message):
    """Fired when a pair of cards is matched in the flip card game."""

    def __init__(self, sender: Widget, value: str) -> None:
        try:
            super().__init__(sender)  # type: ignore[arg-type]
        except TypeError:
            super().__init__()
        self._origin = sender
        self.value = value

    @property
    def origin(self) -> Widget:
        """Widget that emitted the message."""
        return self._origin

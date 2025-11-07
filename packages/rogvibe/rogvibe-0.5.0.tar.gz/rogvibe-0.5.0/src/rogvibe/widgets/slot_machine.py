"""Slot machine widgets."""

from __future__ import annotations

import random
from typing import Any

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget

from ..models.messages import SlotAllStopped, SlotReelSpinning, SlotReelStopped
from ..utils.detector import detect_default_participants
from ..constants import MAYBE_VIBER


class SlotMachineReel(Widget):
    """A single reel of the slot machine."""

    DEFAULT_CSS = """
    SlotMachineReel {
        width: 20;
        height: 7;
        border: double $primary;
        content-align: center middle;
        overflow: hidden;
    }
    """

    current_value = reactive("")
    current_index = reactive(0)

    def __init__(self, reel_index: int, items: list[str]) -> None:
        super().__init__()
        self._reel_index = reel_index
        self._items = items
        self._is_spinning = False
        self._timer: Any | None = None
        self._target_value: str | None = None
        self._spin_count = 0
        self.current_index = random.randrange(len(self._items)) if self._items else 0
        self.current_value = self._items[self.current_index] if self._items else "?"

    def render(self) -> Text:
        """Render the reel with scrolling effect showing 3 items."""
        if not self._items:
            return Text("???", justify="center", style="bold yellow")

        # Show 3 items: 1 before, current, 1 after
        indices = [
            (self.current_index - 1) % len(self._items),
            self.current_index,
            (self.current_index + 1) % len(self._items),
        ]

        items = [self._items[i] for i in indices]

        # Create a vertical scrolling effect
        lines = [
            items[0],  # -1
            "┄" * 18,
            items[1],  # current (middle)
            "┄" * 18,
            items[2],  # +1
        ]

        content = "\n".join(lines)
        text = Text(content, justify="center")

        # Calculate positions for styling
        line_lengths = [len(line) + 1 for line in lines]  # +1 for newline

        pos = 0
        # Item -1 (dim)
        text.stylize("dim", pos, pos + len(items[0]))
        pos += line_lengths[0]
        pos += line_lengths[1]  # skip separator

        # Current item (highlighted)
        text.stylize("bold yellow on #444444", pos, pos + len(items[1]))
        pos += line_lengths[2]
        pos += line_lengths[3]  # skip separator

        # Item +1 (dim)
        text.stylize("dim", pos, pos + len(items[2]))

        return text

    def start_spin(self, duration_steps: int) -> None:
        """Start spinning the reel."""
        if self._is_spinning:
            return
        self._is_spinning = True
        self._spin_count = 0
        # Choose target index instead of target value
        self._target_index = random.randrange(len(self._items))
        self._target_value = self._items[self._target_index]
        self._total_steps = duration_steps
        self._initial_delay = 0.03  # Start fast
        self._schedule_spin()

    def _schedule_spin(self) -> None:
        # Calculate dynamic delay - start fast, end slow
        progress = self._spin_count / self._total_steps
        # Use quadratic easing for smooth deceleration
        delay = self._initial_delay + (progress**2) * 0.15
        self._timer = self.set_timer(delay, self._advance_spin)

    def _advance_spin(self) -> None:
        self._spin_count += 1
        # Advance to next index for scrolling effect
        self.current_index = (self.current_index + 1) % len(self._items)
        self.current_value = self._items[self.current_index]
        self.post_message(SlotReelSpinning(self, self._reel_index, self.current_value))

        if self._spin_count >= self._total_steps:
            self._is_spinning = False
            # Set to target index
            self.current_index = self._target_index
            self.current_value = self._items[self.current_index]
            self.post_message(
                SlotReelStopped(self, self._reel_index, self.current_value)
            )
        else:
            self._schedule_spin()

    @property
    def is_spinning(self) -> bool:
        return self._is_spinning

    @property
    def value(self) -> str:
        return self.current_value


class SlotMachineLever(Widget):
    """A lever widget for the slot machine."""

    DEFAULT_CSS = """
    SlotMachineLever {
        width: 8;
        height: auto;
        align: center middle;
    }
    """

    lever_state = reactive("up")  # "up" or "down"

    def render(self) -> Text:
        """Render the lever."""
        if self.lever_state == "up":
            lever_art = """
 ║
 ║
 ●"""
        else:
            lever_art = """

 ║
 ║
 ║
 ●"""
        return Text(lever_art, justify="center", style="bright_cyan")


class SlotMachineWidget(Widget):
    """The complete slot machine with 3 reels and a lever."""

    DEFAULT_CSS = """
    SlotMachineWidget {
        width: auto;
        height: auto;
        align: center middle;
    }
    SlotMachineWidget Horizontal {
        width: auto;
        height: auto;
        align: center middle;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        # Use detected providers, fallback to MAYBE_VIBER if none found
        detected_providers = detect_default_participants()
        self._items = detected_providers if detected_providers else list(MAYBE_VIBER)
        self._reels = [
            SlotMachineReel(0, self._items),
            SlotMachineReel(1, self._items),
            SlotMachineReel(2, self._items),
        ]
        self._lever = SlotMachineLever()
        self._is_spinning = False
        self._stopped_count = 0
        self._results: list[str] = []

    def compose(self) -> ComposeResult:
        """Compose the slot machine layout with horizontal reels."""
        with Horizontal():
            yield self._reels[0]
            yield self._reels[1]
            yield self._reels[2]
            yield self._lever

    def start_spin(self) -> None:
        """Start spinning all reels with staggered stops."""
        if self._is_spinning:
            return

        self._is_spinning = True
        self._stopped_count = 0
        self._results = []

        # Animate lever pull
        self._lever.lever_state = "down"
        self.refresh()

        # Use a timer to return lever after delay
        def return_lever():
            self._lever.lever_state = "up"
            self.refresh()

        self.set_timer(0.5, return_lever)

        # Start spinning all reels
        for i, reel in enumerate(self._reels):
            # Each reel spins for a different duration (staggered)
            duration = random.randint(30, 50) + i * 20
            reel.start_spin(duration)

    def on_slot_reel_stopped(self, message: SlotReelStopped) -> None:
        """Handle a reel stopping."""
        self._stopped_count += 1
        self._results.append(message.value)

        if self._stopped_count == 3:
            self._is_spinning = False
            self.post_message(SlotAllStopped(self, self._results))

    @property
    def is_spinning(self) -> bool:
        return self._is_spinning

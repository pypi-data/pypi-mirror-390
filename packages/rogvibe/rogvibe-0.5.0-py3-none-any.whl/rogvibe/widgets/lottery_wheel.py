"""Lottery wheel widget."""

from __future__ import annotations

import random
from typing import Any, Sequence

from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from ..constants import DICE_EMOJI, DICE_FACES, TARGET_EMOJI
from ..models.messages import SpinFinished, SpinTick


class LotteryWheel(Widget):
    """Simple wheel that highlights one participant at a time.

    Layout auto-adjusts by participant count with a minimum of 4:
    - 4 or fewer (but >=4): 2x2 grid (4 visible slots)
    - 5 to 8: 3x3 grid with a bullseye center (8 visible slots)
    """

    DEFAULT_CSS = """
    LotteryWheel {
        width: 50;
        height: auto;
    }
    """

    current_index = reactive(0)
    current_dice = reactive("🎯")
    celebration_border_color = reactive("yellow")  # For flashing animation

    def __init__(self, participants: Sequence[str]) -> None:
        if not participants or len(participants) < 4:
            raise ValueError("Provide at least 4 participants.")

        super().__init__()

        # Determine grid size and visible capacity
        self._grid_size = 2 if len(participants) <= 4 else 3
        self._capacity = 4 if self._grid_size == 2 else 8
        self._cell_width = 12 if self._grid_size == 2 else 14

        limited = list(participants[: self._capacity])
        self._participants = limited
        self._participant_count = len(self._participants)
        extra = len(participants) - len(self._participants)
        self._truncated = extra > 0
        if self._truncated:
            self._extra_count = extra
        # Slot indices around the perimeter in clockwise order
        self._layout_slots: list[int | None] = [
            idx if idx < self._participant_count else None
            for idx in range(self._capacity)
        ]
        self._is_spinning = False
        self._steps_remaining = 0
        self._initial_steps = 0
        self._delay = 0.08
        self._timer: Any | None = None
        self._dice_faces = DICE_FACES
        self._emoji_dice = DICE_EMOJI

    def on_mount(self) -> None:
        """Adjust width for nicer layout depending on grid size."""
        # Narrower width for 2x2 so it doesn't look sparse
        self.styles.width = 36 if self._grid_size == 2 else 50

    def render(self) -> Panel:
        """Render participants in a faux wheel layout."""
        table = Table.grid(expand=False, padding=(0, 2))

        if self._grid_size == 2:
            # 2x2 grid: slots arranged clockwise
            table.add_row(self._render_cell(0), self._render_cell(1))
            table.add_row(self._render_cell(3), self._render_cell(2))
        else:
            # 3x3 grid: perimeter slots with bullseye center
            table.add_row(
                self._render_cell(0), self._render_cell(1), self._render_cell(2)
            )
            table.add_row(
                self._render_cell(7),
                Panel(
                    Text(self.current_dice, justify="center"),
                    box=box.MINIMAL,
                    padding=(0, 2),
                ),
                self._render_cell(3),
            )
            table.add_row(
                self._render_cell(6), self._render_cell(5), self._render_cell(4)
            )

        return Panel(
            Align.center(table),
            title="Rogvibe",
            border_style="bright_cyan",
            box=box.ROUNDED,
        )

    def _render_cell(self, slot_index: int) -> Panel:
        participant_index = self._layout_slots[slot_index]
        if participant_index is None:
            return Panel(
                "",
                box=box.SQUARE,
                width=self._cell_width,
                padding=(0, 1),
                border_style="dim",
            )

        participant = self._participants[participant_index]
        label = Text(participant, justify="center", overflow="ellipsis")
        highlight = participant_index == self.current_index
        # Use celebration_border_color for highlighted cell
        border = self.celebration_border_color if highlight else "dark_cyan"
        style = "black on yellow" if highlight else "white on dark_blue"
        label.stylize(style)
        return Panel(
            label,
            box=box.SQUARE,
            width=self._cell_width,
            padding=(0, 1),
            border_style=border,
        )

    def start_spin(self) -> None:
        if self._is_spinning:
            return

        self._is_spinning = True
        self.current_dice = DICE_EMOJI
        self._initial_steps = random.randint(
            self._participant_count * 4, self._participant_count * 7
        )
        target_index = random.randrange(self._participant_count)
        offset = (target_index - self.current_index) % self._participant_count
        self._steps_remaining = self._initial_steps + offset
        self._delay = 0.05
        self._schedule_tick()

    def _schedule_tick(self) -> None:
        self._timer = self.set_timer(self._delay, self._advance)

    def _advance(self) -> None:
        self.current_index = (self.current_index + 1) % self._participant_count
        self._steps_remaining -= 1
        dice_face = random.choice(self._dice_faces)
        self.current_dice = dice_face
        self.post_message(SpinTick(self, dice_face))

        if self._steps_remaining <= 0:
            self._is_spinning = False
            self.current_dice = TARGET_EMOJI
            winner = self._participants[self.current_index]
            self.post_message(SpinFinished(self, winner))
            return

        progress = 1 - self._steps_remaining / self._initial_steps
        self._delay = 0.05 + progress * progress * 0.25
        self._schedule_tick()

    @property
    def is_spinning(self) -> bool:
        return self._is_spinning

    @property
    def truncated(self) -> bool:
        return self._truncated

    @property
    def extra_count(self) -> int:
        return getattr(self, "_extra_count", 0)

    @property
    def visible_capacity(self) -> int:
        """Number of names that can be shown at once based on layout."""
        return self._capacity

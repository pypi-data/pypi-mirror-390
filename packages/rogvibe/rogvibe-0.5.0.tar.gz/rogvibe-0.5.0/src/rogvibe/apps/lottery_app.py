"""Lottery wheel application."""

from __future__ import annotations

from typing import Any, Sequence

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Static

from ..constants import SPECIAL_PARTICIPANTS
from ..models.messages import SpinFinished, SpinTick
from ..utils.executor import execute_command
from ..widgets.lottery_wheel import LotteryWheel


class LotteryApp(App):
    """App wiring the wheel and some helper text together."""

    CSS = """
    Screen {
        align: center middle;
        background: #1b1e28;
    }

    #layout {
        width: auto;
        align: center middle;
        padding: 1 4;
        border: tall #3f6fb5;
    }

    #instructions {
        content-align: center middle;
        text-style: bold;
    }

    #warning {
        color: #ffcc66;
        text-style: italic;
        margin-top: 1;
    }

    #result {
        height: auto;
        content-align: center middle;
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("space", "spin", "Spin"),
        ("enter", "execute", "Run"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, participants: Sequence[str]) -> None:
        super().__init__()
        self._participants = list(participants)
        self._wheel = LotteryWheel(self._participants)
        self._result = Static(id="result")
        self._pending_command: str | None = None
        self._celebration_timer: Any | None = None
        self._celebration_frame = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="layout"):
            # Check if all participants are "handy"
            if all(p == "handy" for p in self._participants):
                instruction_text = "✍️ You're a hero who hand-writes the code. Press Space to spin; press q to quit."
            else:
                instruction_text = "Press Space to spin; press Enter to run the viber; press q to quit."

            yield Static(
                instruction_text,
                id="instructions",
            )
            if self._wheel.truncated:
                yield Static(
                    f"⚠️ Showing only the first {self._wheel.visible_capacity} names; the remaining {self._wheel.extra_count} are ignored.",
                    id="warning",
                )
            yield self._wheel
            yield self._result
        yield Footer()

    def action_spin(self) -> None:
        if not self._wheel.is_spinning:
            self._pending_command = None
            # Stop any ongoing celebration animation
            if self._celebration_timer:
                self._celebration_timer.stop()
                self._celebration_timer = None
            # Reset wheel border color
            self._wheel.celebration_border_color = "yellow"
            self._result.update("🎲 Spinning...")
            self._wheel.start_spin()

    def on_spin_tick(self, message: SpinTick) -> None:
        """Update the spinning message with animated dice."""
        dice_emoji_map = {"⚀": "⚀", "⚁": "⚁", "⚂": "⚂", "⚃": "⚃", "⚄": "⚄", "⚅": "⚅"}
        dice_display = dice_emoji_map.get(message.dice_face, "🎲")
        self._result.update(f"{dice_display} Spinning...")

    def _animate_celebration(self) -> None:
        """Animate celebration for lucky/handy/claude winners."""
        from ..constants import BORDER_COLORS, CELEBRATION_EMOJIS, ANIMATION_COLORS

        # Cycle through different emojis and colors
        emoji = CELEBRATION_EMOJIS[self._celebration_frame % len(CELEBRATION_EMOJIS)]

        # Update wheel border color to flash
        border_color = BORDER_COLORS[self._celebration_frame % len(BORDER_COLORS)]
        self._wheel.celebration_border_color = border_color

        # Create animated text with changing colors
        current_winner = self._pending_command or "winner"
        if current_winner == "handy":
            base_text = f"{emoji} viber: {current_winner} {emoji}\n✍️  You're a hero who hand-writes the code. Press Space to spin again, or q to quit."
        elif current_winner == "lucky":
            base_text = f"{emoji} viber: {current_winner} {emoji}\n🍀 Lucky winner! Press Space to spin again, or q to quit."
        elif current_winner == "claude":
            base_text = f"{emoji} viber: {current_winner} {emoji}\n🤖 AI Assistant! Press Space to spin again, or q to quit."
        else:
            base_text = f"{emoji} viber: {current_winner} {emoji}\n🎉 Special winner! Press Space to spin again, or q to quit."

        text = Text(base_text)
        color = ANIMATION_COLORS[self._celebration_frame % len(ANIMATION_COLORS)]
        # Apply color to the emoji parts
        text.stylize(f"bold {color}", 0, len(emoji))

        self._result.update(text)
        self._celebration_frame += 1

        # Continue animation for 15 frames (~1.5 seconds)
        if self._celebration_frame < 15:
            self._celebration_timer = self.set_timer(0.1, self._animate_celebration)
        else:
            # Animation done, reset border color and show final message
            self._wheel.celebration_border_color = "yellow"
            if current_winner == "handy":
                if all(p == "handy" for p in self._participants):
                    final_text = f"🎉 viber: {current_winner}\n✍️  You're a hero who hand-writes the code. Press Space to spin again, or q to quit."
                else:
                    final_text = f"🎉 viber: {current_winner}\n✍️  You're a hero who hand-writes the code. Press Space to spin again, or q to quit."
            elif current_winner == "lucky":
                final_text = f"🎉 viber: {current_winner}\n🍀 Lucky winner! Press Space to spin again, or q to quit."
            elif current_winner == "claude":
                final_text = f"🎉 viber: {current_winner}\n🤖 AI Assistant! Press Space to spin again, or q to quit."
            else:
                final_text = f"🎉 viber: {current_winner}\n🎉 Special winner! Press Space to spin again, or q to quit."
            self._result.update(final_text)

    def on_spin_finished(self, message: SpinFinished) -> None:
        self._pending_command = message.winner
        # If it's "lucky" or "handy" or "claude", don't allow command execution, but show animation
        if message.winner in SPECIAL_PARTICIPANTS:
            # Start celebration animation
            self._celebration_frame = 0
            self._animate_celebration()
        else:
            self._result.update(
                f"🎉 viber: {message.winner}\n↩️  Press Enter to run and exit, or q to quit."
            )

    def action_execute(self) -> None:
        if not self._pending_command:
            return
        if self._pending_command in ("lucky", "handy"):
            return
        execute_command(self._pending_command, self)

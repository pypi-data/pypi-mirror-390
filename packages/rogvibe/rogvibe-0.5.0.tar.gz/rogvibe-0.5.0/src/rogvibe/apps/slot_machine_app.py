"""Slot machine application."""

from __future__ import annotations

from collections import Counter
from typing import Any

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Static

from ..models.messages import SlotAllStopped
from ..utils.executor import execute_command
from ..widgets.slot_machine import SlotMachineWidget


class SlotMachineApp(App):
    """Slot machine app."""

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
        margin-bottom: 1;
    }

    #result {
        height: auto;
        content-align: center middle;
        margin-top: 1;
        color: #ffcc66;
        text-style: bold;
    }

    #fireworks {
        height: 15;
        width: 100%;
        content-align: center middle;
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("space", "spin", "Pull Lever"),
        ("enter", "execute", "Run"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._slot_machine = SlotMachineWidget()
        self._result = Static(id="result")
        self._fireworks_display = Static(id="fireworks")
        self._pending_command: str | None = None
        self._fireworks_timer: Any | None = None
        self._fireworks_frame = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="layout"):
            yield Static(
                "🎰 Press Space to pull the lever; press Enter to run the viber; press q to quit.",
                id="instructions",
            )
            yield self._slot_machine
            yield self._fireworks_display
            yield self._result
        yield Footer()

    def action_spin(self) -> None:
        """Handle spin action."""
        if not self._slot_machine.is_spinning:
            self._pending_command = None
            # Stop any ongoing fireworks
            if self._fireworks_timer:
                self._fireworks_timer.stop()
                self._fireworks_timer = None
            self._fireworks_display.update("")
            # Reset reel colors when starting a new spin
            for reel in self._slot_machine._reels:
                reel.styles.border = ("double", "ansi_bright_magenta")
            self._result.update("Pulling lever...")
            self._slot_machine.start_spin()

    def _animate_fireworks(self) -> None:
        """Animate fireworks display frame by frame."""
        fireworks_frames = [
            # Frame 0 - Initial burst
            """
                    *
                *       *
            *               *
                *       *
                    *
            """,
            # Frame 1 - Expanding
            """
                *       *
            *               *
        *                       *
            *               *
                *       *
            """,
            # Frame 2 - Peak explosion
            """
            *   ✦       ✦   *
        *   ✦   ★   ★   ✦   *
    *   ✦   ★   ✦   ★   ✦   *
        *   ✦   ★   ★   ✦   *
            *   ✦       ✦   *
            """,
            # Frame 3 - Sparkling
            """
                ✦   *   ✦
            *   ★   ✦   ★   *
        ✦   ★   ✦   ★   ✦
            *   ★   ✦   ★   *
                ✦   *   ✦
            """,
            # Frame 4 - Fading
            """
                    ·
                ·       ·
            ·       ·       ·
                ·       ·
                    ·
            """,
            # Frame 5 - Multiple bursts
            """
        *   ✦           ✦   *
            ★   *   ★
    ✦           ✦           ✦
            ★   *   ★
        *   ✦           ✦   *
            """,
            # Frame 6 - Grand finale
            """
    ★   ✦   *   ✦   *   ✦   ★
        *   ★   ✦   ★   *
    ✦   ★   ✦   ★   ✦   ★   ✦
        *   ★   ✦   ★   *
    ★   ✦   *   ✦   *   ✦   ★
            """,
            # Frame 7 - Sparkles
            """
            ·   ✦   ·
        ✦       ★       ✦
    ·       ✦   ·   ✦       ·
        ✦       ★       ✦
            ·   ✦   ·
            """,
        ]
        # Apply colors to make it more vibrant - use valid Rich color names
        from ..constants import ANIMATION_COLORS

        frame_text = fireworks_frames[self._fireworks_frame % len(fireworks_frames)]
        # Create colored text
        text = Text(frame_text, justify="center")
        color = ANIMATION_COLORS[self._fireworks_frame % len(ANIMATION_COLORS)]
        text.stylize(color)
        self._fireworks_display.update(text)

        # Make slot borders flash with different colors
        border_colors = [
            "yellow",
            "ansi_bright_red",
            "ansi_bright_magenta",
            "ansi_bright_cyan",
            "ansi_bright_yellow",
        ]
        border_styles = ["heavy", "double", "heavy", "double"]
        border_color = border_colors[self._fireworks_frame % len(border_colors)]
        border_style = border_styles[self._fireworks_frame % len(border_styles)]

        for reel in self._slot_machine._reels:
            reel.styles.border = (border_style, border_color)

        self._fireworks_frame += 1
        # Continue animation for a while (20 frames = ~2 seconds)
        if self._fireworks_frame < 20:
            self._fireworks_timer = self.set_timer(0.1, self._animate_fireworks)
        else:
            # Animation done, clear display and reset borders
            self._fireworks_display.update("")
            for reel in self._slot_machine._reels:
                reel.styles.border = ("heavy", "yellow")

    def on_slot_all_stopped(self, message: SlotAllStopped) -> None:
        """Handle all reels stopped."""
        results = message.results
        # Count occurrences of each result
        counts = Counter(results)
        # Check if all three are the same - JACKPOT!
        if len(set(results)) == 1:
            winner = results[0]
            self._pending_command = winner
            # Highlight all reels with yellow color for JACKPOT
            for reel in self._slot_machine._reels:
                reel.styles.border = ("heavy", "yellow")
            # Start fireworks animation!
            self._fireworks_frame = 0
            self._animate_fireworks()
            self._result.update(
                f"🎉🎉🎉 JACKPOT! All three show: {winner} 🎉🎉🎉\n"
                f"↩️  Press Enter to run '{winner}' and exit, or q to quit."
            )
        # Check if two are the same
        elif max(counts.values()) == 2:
            # Find the value that appears twice
            winner = [item for item, count in counts.items() if count == 2][0]
            self._pending_command = winner
            # Highlight matching reels
            for i, reel in enumerate(self._slot_machine._reels):
                if results[i] == winner:
                    reel.styles.border = ("heavy", "yellow")
                else:
                    reel.styles.border = ("double", "ansi_bright_magenta")
            result_text = " | ".join(results)
            self._result.update(
                f"✨ Two match: {winner}! Results: {result_text}\n"
                f"↩️  Press Enter to run '{winner}' and exit, or q to quit."
            )
        else:
            # All different - no match
            # Reset reel colors
            for reel in self._slot_machine._reels:
                reel.styles.border = ("double", "ansi_bright_magenta")
            result_text = " | ".join(results)
            self._result.update(
                f"Results: {result_text}\n"
                f"🔄 Press Space to spin again, or q to quit."
            )

    def action_execute(self) -> None:
        """Execute the winner command."""
        if not self._pending_command:
            return
        # Don't execute special participants like "lucky" and "handy"
        from ..constants import SPECIAL_PARTICIPANTS

        if self._pending_command in SPECIAL_PARTICIPANTS:
            return
        execute_command(self._pending_command, self)

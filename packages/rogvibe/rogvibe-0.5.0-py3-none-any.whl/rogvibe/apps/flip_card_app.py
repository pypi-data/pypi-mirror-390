"""Flip card game application."""

from __future__ import annotations

from typing import Any

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Static

from ..models.messages import AllCardsMatched, PairMatched
from ..utils.detector import detect_default_participants
from ..utils.executor import execute_command
from ..widgets.flip_card import FlipCardGrid


class FlipCardApp(App):
    """Flip card matching game app."""

    CSS = """
    Screen {
        align: center middle;
        background: #1b1e28;
    }

    #layout {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1 2;
        border: tall #3f6fb5;
    }

    #instructions {
        content-align: center middle;
        text-style: bold;
        margin-bottom: 1;
    }

    FlipCardGrid {
        width: 100%;
        height: auto;
    }

    #card_grid {
        grid-size: 4;
        grid-gutter: 1 2;
    }

    Card {
        width: 18;
        height: 7;
        border: heavy #3f6fb5;
        content-align: center middle;
        text-style: bold;
    }

    Card.flipped {
        border: heavy yellow;
        background: #2a2d3a;
    }

    Card.matched {
        border: heavy green;
        background: #1f4d1f;
    }

    Card:hover {
        border: heavy cyan;
    }

    #result {
        height: auto;
        content-align: center middle;
        margin-top: 1;
        color: #ffcc66;
        text-style: bold;
    }

    #celebration {
        height: 8;
        width: 100%;
        content-align: center middle;
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("r", "reset", "Reset"),
        ("enter", "execute", "Run"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        # Get participants from detector
        participants = detect_default_participants()
        if not participants or len(participants) < 8:
            # Need exactly 8 items for 4x4 grid (each appears twice)
            participants = [
                "kimi",
                "claude",
                "cursor",
                "code",
                "gemini",
                "amp",
                "lucky",
                "handy",
            ]
        # Take only first 8
        self._participants = participants[:8]
        self._grid = FlipCardGrid(self._participants)
        self._result = Static(id="result")
        self._celebration_display = Static(id="celebration")
        self._pending_command: str | None = None
        self._celebration_timer: Any | None = None
        self._celebration_frame = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="layout"):
            yield Static(
                "🃏 Click cards to flip! Match pairs to win.",
                id="instructions",
            )
            yield self._grid
            yield self._celebration_display
            yield self._result
        yield Footer()

    def action_reset(self) -> None:
        """Reset the game."""
        self._grid.reset()
        self._result.update("")
        self._celebration_display.update("")
        self._pending_command = None
        if self._celebration_timer:
            self._celebration_timer.stop()
            self._celebration_timer = None

    def _animate_celebration(self) -> None:
        """Animate celebration when all cards are matched."""
        celebration_frames = [
            # Frame 0
            """
            🎉  🎊  🎉
        ✨  🌟  ⭐  🌟  ✨
            🎉  🎊  🎉
            """,
            # Frame 1
            """
        ⭐  ✨  🌟  ✨  ⭐
            🎊  🎉  🎊
        ⭐  ✨  🌟  ✨  ⭐
            """,
            # Frame 2
            """
            🌟  ⭐  🌟
        🎉  ✨  💫  ✨  🎉
            🌟  ⭐  🌟
            """,
            # Frame 3
            """
        💫  🎊  ⭐  🎊  💫
            ✨  🎉  ✨
        💫  🎊  ⭐  🎊  💫
            """,
        ]

        from ..constants import ANIMATION_COLORS

        frame_text = celebration_frames[
            self._celebration_frame % len(celebration_frames)
        ]
        text = Text(frame_text, justify="center")
        color = ANIMATION_COLORS[self._celebration_frame % len(ANIMATION_COLORS)]
        text.stylize(f"bold {color}")
        self._celebration_display.update(text)

        self._celebration_frame += 1
        if self._celebration_frame < 16:
            self._celebration_timer = self.set_timer(0.15, self._animate_celebration)
        else:
            self._celebration_display.update("")

    def on_all_cards_matched(self, message: AllCardsMatched) -> None:
        """Handle all cards matched event."""
        winner = message.winner
        self._pending_command = winner

        # Start celebration animation
        self._celebration_frame = 0
        self._animate_celebration()

        self._result.update(
            f"🎉🎉🎉 All cards matched! Winner: {winner} 🎉🎉🎉\n"
            f"↩️  Press Enter to run '{winner}' and exit, or R to play again, or q to quit."
        )

    def on_pair_matched(self, message: PairMatched) -> None:
        """Handle a pair matched event."""
        value = message.value
        self._pending_command = value
        self._result.update(
            f"✨ Pair matched: {value}!\n"
            f"↩️  Press Enter to run '{value}' and exit, or continue playing."
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

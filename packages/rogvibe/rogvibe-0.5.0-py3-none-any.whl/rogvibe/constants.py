"""Constants and configuration for rogvibe."""

from __future__ import annotations

# Fallback participant names
FALLBACK_DEFAULTS: list[str] = [
    "handy",
    "handy",
    "handy",
    "handy",
]

# List of potential viber commands to detect on the system
# add more here PR welcome
MAYBE_VIBER: list[str] = [
    "kimi",
    "claude",
    "gemini",
    "codex",
    "code",
    "cursor",
    "amp",
    "opencode",
]

# Animation settings
ANIMATION_COLORS: list[str] = ["yellow", "red", "magenta", "cyan", "white"]
BORDER_COLORS: list[str] = ["yellow", "red", "magenta", "cyan", "green"]
CELEBRATION_EMOJIS: list[str] = ["✨", "🌟", "⭐", "💫", "🎉", "🎊", "🎈"]

# Dice faces
DICE_FACES: list[str] = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
DICE_EMOJI: str = "🎲"
TARGET_EMOJI: str = "🎯"

# Special participants
SPECIAL_PARTICIPANTS: set[str] = {"lucky", "handy"}

"""Command execution utilities."""

from __future__ import annotations

import os
import shlex
import shutil
import sys
from contextlib import nullcontext
from typing import Any


def execute_command(winner: str, app: Any) -> None:
    """Execute the winner as a command and exit the app.

    Args:
        winner: The command to execute
        app: The Textual app instance (for suspend and exit)

    - Parses the winner string with shlex to support simple arguments.
    - If command is not on PATH, exits with code 127.
    - On success, replaces the current process using os.execvp.
    """
    # if is code or cursor, automatically add '.' argument
    if winner in ("code", "cursor"):
        winner = f"{winner} ."

    argv = shlex.split(winner)
    if not argv:
        app.exit(0)
        return

    cmd = argv[0]
    if shutil.which(cmd) is None:
        print(f"[rogvibe] Command not found: {cmd}")
        app.exit(127)
        return

    # Replace current process with the chosen command.
    # Use Textual's suspend() to restore terminal state before exec.
    ctx = app.suspend() if hasattr(app, "suspend") else nullcontext()
    try:
        with ctx:
            os.execvp(cmd, argv)
    except FileNotFoundError:
        print(f"[rogvibe] Command not found: {cmd}", file=sys.stderr)
        app.exit(127)
    except PermissionError:
        print(f"[rogvibe] Permission denied: {cmd}", file=sys.stderr)
        app.exit(126)
    except OSError as e:
        print(f"[rogvibe] Failed to exec '{cmd}': {e}", file=sys.stderr)
        app.exit(1)

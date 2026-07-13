"""
Named keystrokes (arrows, Enter, Tab, Ctrl combos) carry a ``name`` such as "KEY_DOWN",
while printable keys carry none and are their own character.
See :func:`blessed.keyboard.get_curses_keycodes` for the full list of names.
"""

from typing import Final

UP: Final = "KEY_UP"
DOWN: Final = "KEY_DOWN"
LEFT: Final = "KEY_LEFT"
RIGHT: Final = "KEY_RIGHT"
HOME: Final = "KEY_HOME"
END: Final = "KEY_END"

ENTER: Final = "KEY_ENTER"
TAB: Final = "KEY_TAB"
SHIFT_TAB: Final = "KEY_BTAB"
SPACE: Final = " "

CTRL_C: Final = "KEY_CTRL_C"
CTRL_D: Final = "KEY_CTRL_D"
CTRL_Z: Final = "KEY_CTRL_Z"

VIM_MOTIONS: Final = {
    "k": UP,
    "j": DOWN,
    "h": LEFT,
    "l": RIGHT,
}


def vim_motion(key: str) -> str:
    """Translate a vim motion key to its arrow-key token, if it is one."""
    return VIM_MOTIONS.get(key, key)

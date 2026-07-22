"""
Named keystrokes (arrows, Enter, Tab, Ctrl combos) carry a ``name`` such as "KEY_DOWN",
while printable keys carry none and are their own character.
See :func:`blessed.keyboard.get_curses_keycodes` for the full list of names.
"""

from typing import Final

#: Up arrow key.
UP: Final = "KEY_UP"
#: Down arrow key.
DOWN: Final = "KEY_DOWN"
#: Left arrow key.
LEFT: Final = "KEY_LEFT"
#: Right arrow key.
RIGHT: Final = "KEY_RIGHT"
#: Home key.
HOME: Final = "KEY_HOME"
#: End key.
END: Final = "KEY_END"

#: Enter/Return key.
ENTER: Final = "KEY_ENTER"
#: Tab key.
TAB: Final = "KEY_TAB"
#: Shift+Tab (back-tab) key.
SHIFT_TAB: Final = "KEY_BTAB"
#: Space bar.
SPACE: Final = " "

#: Ctrl+C; raises :py:exc:`KeyboardInterrupt` when read.
CTRL_C: Final = "KEY_CTRL_C"
#: Ctrl+D; raises :py:exc:`EOFError` when read.
CTRL_D: Final = "KEY_CTRL_D"
#: Ctrl+Z; treated as end-of-file on Windows.
CTRL_Z: Final = "KEY_CTRL_Z"

_VIM_MOTIONS: Final = {
    "k": UP,
    "j": DOWN,
    "h": LEFT,
    "l": RIGHT,
}


def _vim_motion(key: str) -> str:
    """Translate a vim motion key to its arrow-key token, if it is one."""
    return _VIM_MOTIONS.get(key, key)

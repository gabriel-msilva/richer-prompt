import io

import pytest
import readchar
from rich.console import Console
from rich.theme import Theme

from richer_prompt import Select
from richer_prompt.default_styles import RICHER_PROMPT_STYLES, missing_styles
from tests.utils import simulate


@pytest.mark.parametrize(
    "theme, expected",
    [
        (None, RICHER_PROMPT_STYLES),
        (Theme(RICHER_PROMPT_STYLES), {}),
        (
            Theme({"richer_prompt.cursor": "bold red"}),
            {
                name: style
                for name, style in RICHER_PROMPT_STYLES.items()
                if name != "richer_prompt.cursor"
            },
        ),
    ],
)
def test_missing_styles(theme, expected):
    console = Console(theme=theme)
    assert missing_styles(console) == expected


def test_that_default_styles_are_applied_at_prompt_time():
    buffer = io.StringIO()
    console = Console(
        file=buffer,
        force_terminal=True,
        color_system="standard",
        width=60,
    )

    simulate(Select("Pick:", ["a", "b"], console=console), [readchar.key.ENTER])

    # default cursor style (magenta)
    assert "\x1b[35m" in buffer.getvalue()


def test_that_custom_theme_overrides_defaults():
    buffer = io.StringIO()
    console = Console(
        file=buffer,
        force_terminal=True,
        color_system="standard",
        width=60,
        theme=Theme({"richer_prompt.cursor": "bold red"}),
    )

    simulate(Select("Pick:", ["a", "b"], console=console), [readchar.key.ENTER])

    output = buffer.getvalue()

    assert "\x1b[1;31m" in output  # user's bold red cursor
    assert "\x1b[35m" not in output  # default magenta never rendered

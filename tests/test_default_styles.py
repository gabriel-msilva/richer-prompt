from rich import get_console
from rich.console import Console
from rich.style import Style
from rich.theme import Theme

from richer_prompt.default_styles import RICHER_PROMPT_STYLES


def test_that_default_styles_are_injected():
    console = get_console()

    for name in RICHER_PROMPT_STYLES:
        assert console.get_style(name) is not None


def test_that_custom_theme_overrides_defaults():
    console = Console()

    assert (
        console.get_style("richer_prompt.cursor")
        == RICHER_PROMPT_STYLES["richer_prompt.cursor"]
    )

    console = Console(
        force_terminal=True, theme=Theme({"richer_prompt.cursor": "bold red"})
    )

    assert console.get_style("richer_prompt.cursor") == Style(color="red", bold=True)

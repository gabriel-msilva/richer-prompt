from enum import StrEnum

from rich.style import Style


class Symbols(StrEnum):
    """
    A collection of Unicode symbols for use in prompts.

    References
    ----------
    https://en.wikipedia.org/wiki/List_of_Unicode_characters
    """

    LEFT_POINTER = "❮"  # U+276E
    RIGHT_POINTER = "❯"  # U+276F

    LEFT_ARROW = "←"  # U+2190
    RIGHT_ARROW = "→"  # U+2192
    UP_ARROW = "↑"  # U+2191
    DOWN_ARROW = "↓"  # U+2193

    BULLET = "•"  # U+2022
    MIDDLE_DOT = "·"  # U+00B7

    BALLOT_BOX = "☐"  # U+2610
    BALLOT_BOX_WITH_CHECK = "☑"  # U+2611
    BALLOT_BOX_WITH_X = "☒"  # U+2612

    CHECK_MARK = "✓"  # U+2713
    BALLOT_X = "✗"  # U+2717


RICHER_PROMPT_STYLES: dict[str, Style] = {
    "richer_prompt.title": Style(bold=True),
    "richer_prompt.description": Style(dim=True),
    "richer_prompt.hint": Style(dim=True),
    "richer_prompt.cursor": Style(color="light_steel_blue"),
    "richer_prompt.cursor.submit": Style(bold=True),
    "richer_prompt.choice": Style.null(),
    "richer_prompt.choice.description": Style(dim=True),
    "richer_prompt.checkbox": Style(dim=True),
    "richer_prompt.checkbox.checked": Style(color="green"),
    "richer_prompt.tab.active": Style(color="light_steel_blue", reverse=True),
    "richer_prompt.tab.inactive": Style.null(),
    "richer_prompt.form.answer": Style(color="green"),
}


def inject_styles() -> None:
    from rich import themes
    from rich.default_styles import DEFAULT_STYLES

    for name, style in RICHER_PROMPT_STYLES.items():
        themes.DEFAULT.styles.setdefault(name, style)
        DEFAULT_STYLES.setdefault(name, style)

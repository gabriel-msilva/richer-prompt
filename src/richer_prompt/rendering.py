from typing import Final

from rich.style import Style
from rich.text import Text, TextType

from richer_prompt.choices import Choice

LEFT_POINTER: Final = "❮"
RIGHT_POINTER: Final = "❯"

LEFT_ARROW: Final = "←"
RIGHT_ARROW: Final = "→"
UP_ARROW: Final = "↑"
DOWN_ARROW: Final = "↓"

BULLET: Final = "•"
MIDDLE_DOT: Final = "·"

BALLOT_BOX: Final = "☐"
BALLOT_BOX_WITH_CHECK: Final = "☑"
BALLOT_BOX_WITH_X: Final = "☒"

CHECK_MARK: Final = "✓"
BALLOT_X: Final = "✗"


def cursor_cell(pointer: str, active: bool) -> Text:
    if active:
        return Text(pointer, style="richer_prompt.cursor")

    return Text(" " * len(pointer))


def number_cell(index: int, width: int) -> Text:
    return Text(f"{index + 1}. ".rjust(width + 2), style="richer_prompt.description")


def checkbox_cell(checked: bool) -> Text:
    if checked:
        return Text(f"[{CHECK_MARK}]", style="richer_prompt.checkbox.checked")

    return Text("[ ]", style="richer_prompt.checkbox")


def tab_cell(choice: Choice, focused: bool) -> Text:
    return Text(
        f" {choice.display} ",
        style="richer_prompt.tab.active" if focused else "richer_prompt.tab",
    )


def arrow_cell(arrow: str, dimmed: bool) -> Text:
    return Text(arrow, style="dim" if dimmed else "")


def choice_label(choice: Choice, focused: bool) -> Text:
    label = Text()
    label.append(
        choice.display,
        style="richer_prompt.cursor" if focused else "richer_prompt.choice",
    )

    if choice.description:
        label.append("  ")
        label.append(choice.description, style="richer_prompt.description")

    return label


def ensure_text(value: TextType, default_style: str | Style = "") -> Text:
    return (
        value
        if isinstance(value, Text)
        else Text.from_markup(value, style=default_style)
    )


def format_hint(*parts: str) -> Text:
    return Text(f" {MIDDLE_DOT} ".join(parts), style="richer_prompt.hint")

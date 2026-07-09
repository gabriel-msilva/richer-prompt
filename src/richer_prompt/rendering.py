from typing import Final

from rich.console import Console
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


def resolve_numbered(
    numbered: bool | None, choices: list[Choice], viewport_size: int
) -> bool:
    if numbered is None:
        return len(choices) < 10 and len(choices) <= viewport_size

    return numbered


def resolve_viewport_size(
    viewport_size: int | None, console: Console, overhead: int
) -> int:
    """The explicit size, or however many choice rows fit the terminal height."""
    if viewport_size is None:
        return max(3, console.size.height - overhead)

    return viewport_size


def viewport_slice(total: int, size: int, cursor: int) -> range:
    """Visible index range, keeping the cursor centered where possible."""
    if size >= total:
        return range(total)

    offset = min(max(cursor - (size - 1) // 2, 0), total - size)

    return range(offset, offset + size)


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
    return Text(arrow, style="richer_prompt.hint" if dimmed else "")


def overflow_cell(arrow: str, pointer: str) -> Text:
    return Text(arrow.ljust(len(pointer)), style="richer_prompt.hint")


def pointer_cell(
    pointer: str, focused: bool, index: int, viewport: range, total: int
) -> Text:
    """Cursor column cell: the pointer, an overflow arrow, or a blank."""
    if focused:
        return cursor_cell(pointer, active=True)

    if index == viewport.start and viewport.start > 0:
        return overflow_cell(UP_ARROW, pointer)

    if index == viewport.stop - 1 and viewport.stop < total:
        return overflow_cell(DOWN_ARROW, pointer)

    return cursor_cell(pointer, active=False)


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

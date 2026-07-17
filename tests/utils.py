import textwrap
from typing import Any

from rich.console import Console
from rich.theme import Theme

from richer_prompt.default_styles import RICHER_PROMPT_STYLES
from richer_prompt.prompt import ChoicePrompt, Form
from richer_prompt.session import Widget


def assert_snapshot(
    prompt: ChoicePrompt[Any, Any] | Form,
    expected: str,
    *,
    raw: bool = False,
    **build_kwargs: Any,
) -> None:
    assert_widget_snapshot(prompt._build_widget(**build_kwargs), expected, raw=raw)


def assert_widget_snapshot(
    widget: Widget[Any], expected: str, *, raw: bool = False
) -> None:
    console = Console(
        width=60,
        color_system="standard" if raw else None,
        force_terminal=False,
        theme=Theme(RICHER_PROMPT_STYLES),
    )

    with console.capture() as capture:
        console.print(widget.render())

    rendered = capture.get()

    with console.capture() as capture:
        console.print(
            textwrap.dedent(expected).removeprefix("\n").removesuffix("\n"),
            highlight=False,
        )

    expected = capture.get()

    if raw:
        rendered = repr(rendered)
        expected = repr(expected)

    assert rendered == expected

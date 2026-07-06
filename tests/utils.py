import contextlib
import textwrap
from collections.abc import Sequence
from unittest.mock import patch

from rich.console import Console
from rich.theme import Theme

from richer_prompt.default_styles import RICHER_PROMPT_STYLES
from richer_prompt.session import Widget


@contextlib.contextmanager
def simulate_keys(keys: Sequence[str | BaseException]):
    """
    Pretend to be an interactive terminal delivering the given keys.

    Exception instances in ``keys`` are raised by the key read
    (e.g. ``KeyboardInterrupt`` for Ctrl+C).
    """
    with (
        patch("sys.stdin") as stdin,
        patch("richer_prompt.session.readchar.readkey", side_effect=keys),
    ):
        stdin.isatty.return_value = True
        yield


def simulate(prompt, keys: Sequence[str | BaseException], **kwargs):
    with simulate_keys(keys):
        return prompt(**kwargs)


def assert_snapshot(widget: Widget, expected: str, raw: bool = False) -> None:
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

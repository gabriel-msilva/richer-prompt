import textwrap
from unittest.mock import patch

from rich.console import Console


def simulate(prompt, keys: list[str], **kwargs):
    with patch("richer_prompt.models.readchar.readkey", side_effect=keys):
        return prompt(**kwargs)


def assert_snapshot(prompt, model, expected: str, raw: bool = False) -> None:
    console = Console(
        width=60,
        color_system="standard" if raw else None,
        force_terminal=False,
    )

    with console.capture() as capture:
        console.print(prompt.renderer.render(model))

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

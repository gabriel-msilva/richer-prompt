from collections.abc import Callable
from typing import Protocol, TypeVar

import readchar
from rich.console import Console, RenderableType
from rich.live import Live
from rich.text import Text

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


class Widget(Protocol[T_co]):
    """
    A self-contained per-run component driven by :py:func:`run`.

    ``handle_key`` returns whether the key was consumed, so that a composite
    widget (e.g. a form) can arbitrate keys between itself and its children.
    """

    @property
    def submitted(self) -> bool: ...

    def handle_key(self, key: str) -> bool: ...

    def render(self) -> RenderableType: ...

    def answer(self) -> Text: ...

    def result(self) -> T_co: ...


def run(
    widget: Widget[T],
    console: Console,
    *,
    read_key: Callable[[], str] | None = None,
) -> T:
    # resolved at call time so tests can patch `readchar.readkey`
    if read_key is None:
        read_key = readchar.readkey

    with Live(
        widget.render(),
        console=console,
        auto_refresh=False,
        transient=True,
    ) as live:
        while not widget.submitted:
            widget.handle_key(read_key())
            live.update(widget.render(), refresh=True)

    console.print(widget.answer())

    return widget.result()

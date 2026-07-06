import sys
from collections.abc import Callable
from contextvars import ContextVar
from typing import Final, Protocol, TypeVar

import readchar
from rich.console import Console, RenderableType
from rich.live import Live
from rich.text import Text
from rich.theme import Theme

from richer_prompt.default_styles import missing_styles

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


class NotInteractiveError(RuntimeError):
    """Raised when a prompt is run without an interactive terminal."""


def _eof_keys(platform: str = sys.platform) -> frozenset[str]:
    # Ctrl+Z means EOF only on Windows; on *nix it is the suspend gesture
    if platform == "win32":
        return frozenset({readchar.key.CTRL_D, readchar.key.CTRL_Z})

    return frozenset({readchar.key.CTRL_D})


EOF_KEYS: Final = _eof_keys()


_key_source_override: ContextVar[Callable[[], str] | None] = ContextVar(
    "richer_prompt_key_source_override", default=None
)


def _default_key_source() -> Callable[[], str]:
    """The real keyboard (requires an interactive terminal), unless overridden."""
    override = _key_source_override.get()
    if override is not None:
        return override

    if sys.stdin is None or not sys.stdin.isatty():
        raise NotInteractiveError(
            "prompts require an interactive terminal, but stdin is not a TTY"
        )

    return readchar.readkey


def run(widget: Widget[T], console: Console) -> T:
    read_key = _default_key_source()
    theme = Theme(missing_styles(console), inherit=False)

    with console.use_theme(theme):
        with Live(
            widget.render(),
            console=console,
            auto_refresh=False,
            transient=True,
        ) as live:
            while not widget.submitted:
                key = read_key()
                if key in EOF_KEYS:
                    raise EOFError("end of input")

                widget.handle_key(key)
                live.update(widget.render(), refresh=True)

        console.print(widget.answer())

    return widget.result()

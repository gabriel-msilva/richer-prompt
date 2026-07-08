import sys
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager, nullcontext
from contextvars import ContextVar
from typing import Final, Protocol, TypeVar

from blessed import Terminal
from blessed.keyboard import Keystroke
from rich.console import Console, RenderableType
from rich.live import Live
from rich.text import Text
from rich.theme import Theme

from richer_prompt import keys
from richer_prompt.default_styles import missing_styles

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)

EOF_KEYS: Final = (
    frozenset({keys.CTRL_D, keys.CTRL_Z})
    if sys.platform == "win32"
    else frozenset({keys.CTRL_D})
)

_key_source_override: ContextVar[Callable[[], str] | None] = ContextVar(
    "richer_prompt_key_source_override", default=None
)


class NotInteractiveError(RuntimeError):
    """Raised when a prompt is run without an interactive terminal."""


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


def run(widget: Widget[T], console: Console) -> T:
    theme = Theme(missing_styles(console), inherit=False)

    with _key_source() as read_key, console.use_theme(theme):
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


def _key_source() -> AbstractContextManager[Callable[[], str]]:
    """The real keyboard, unless a test has overridden the source."""
    override = _key_source_override.get()
    if override is not None:
        return nullcontext(override)

    return _real_key_source()


@contextmanager
def _real_key_source() -> Iterator[Callable[[], str]]:
    """Read keys from the real keyboard; requires an interactive terminal."""
    if sys.stdin is None or not sys.stdin.isatty():
        raise NotInteractiveError(
            "prompts require an interactive terminal, but stdin is not a TTY"
        )

    term = Terminal()
    with term.cbreak():
        yield lambda: _to_token(term.inkey())


def _to_token(keystroke: Keystroke) -> str:
    """
    Map a blessed keystroke to a token from :mod:`richer_prompt.keys`.

    Named keystrokes (arrows, Enter, Tab, Ctrl combos) carry a ``name`` such
    as "KEY_DOWN", while printable keys carry none and are their own character.
    See :func:`blessed.keyboard.get_curses_keycodes` for the full list of names.
    """
    return keystroke.name or str(keystroke)

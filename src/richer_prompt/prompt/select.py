import dataclasses
from collections.abc import Iterable
from typing import Final, Generic, TypeVar

from rich.console import Console, Group
from rich.text import Text, TextType

from richer_prompt import keys
from richer_prompt.choices import Choice
from richer_prompt.prompt.base import ChoicePrompt
from richer_prompt.rendering import (
    DOWN_ARROW,
    RIGHT_POINTER,
    UP_ARROW,
    choice_label,
    format_hint,
    number_cell,
    pointer_cell,
    resolve_numbered,
    resolve_viewport_size,
    viewport_slice,
)
from richer_prompt.session import CONSUMED, IGNORED, Done, KeyOutcome

T = TypeVar("T")

# Rows rendered around the choices: message, blank lines, hint, and a margin line
VIEWPORT_OVERHEAD: Final = 5


@dataclasses.dataclass(slots=True)
class SelectWidget(Generic[T]):
    message: Text
    choices: list[Choice[T]]
    cursor: int
    cursor_pointer: str
    numbered: bool
    viewport_size: int
    show_hint: bool

    # Index committed at submit time. The cursor is only navigational, so the
    # answer must be snapshotted: revisiting a Form step and moving the cursor
    # (without a fresh Enter) leaves the recorded choice unchanged.
    _selected: int | None = dataclasses.field(init=False, default=None)

    def __post_init__(self):
        if self.cursor < 0 or self.cursor >= len(self.choices):
            raise ValueError(f"Index '{self.cursor}' is out of range")

        if self.viewport_size < 3:
            raise ValueError(f"Viewport size '{self.viewport_size}' must be at least 3")

    @property
    def current(self) -> Choice[T]:
        return self.choices[self.cursor]

    @property
    def selected(self) -> Choice[T] | None:
        if self._selected is None:
            return None

        return self.choices[self._selected]

    @property
    def answered(self) -> bool:
        return self._selected is not None

    def submit(self) -> None:
        """Commit the choice under the cursor as this widget's answer."""
        self._selected = self.cursor

    def move(self, delta: int) -> None:
        self.cursor = (self.cursor + delta) % len(self.choices)

    def handle_key(self, key: str) -> KeyOutcome:
        key = keys.vim_motion(key)

        match key:
            case keys.DOWN:
                self.move(1)
            case keys.UP:
                self.move(-1)
            case keys.HOME:
                self.cursor = 0
            case keys.END:
                self.cursor = len(self.choices) - 1
            case keys.ENTER:
                if self.current.disabled:
                    return CONSUMED
                self.submit()
                return Done(self.result())
            case _ if self.numbered and key.isdecimal():
                n = int(key) - 1
                if 0 <= n < len(self.choices) and not self.choices[n].disabled:
                    self.cursor = n
                    self.submit()
                    return Done(self.result())
            case _:
                return IGNORED

        return CONSUMED

    def render(self) -> Group:
        rows: list[Text] = []

        if self.message:
            rows.append(self.message)
            rows.append(Text())

        number_width = len(str(len(self.choices)))
        viewport = viewport_slice(len(self.choices), self.viewport_size, self.cursor)

        for i in viewport:
            is_focused = i == self.cursor
            is_selected = i == self._selected

            pointer = pointer_cell(
                self.cursor_pointer, is_focused, i, viewport, len(self.choices)
            )

            rows.append(
                Text.assemble(
                    pointer,
                    " ",
                    number_cell(i, number_width) if self.numbered else Text(),
                    choice_label(self.choices[i], is_focused, is_selected),
                )
            )

        if self.show_hint:
            rows.append(Text())
            rows.append(
                format_hint(
                    f"{UP_ARROW}{DOWN_ARROW} to navigate",
                    "Enter to select",
                )
            )

        return Group(*rows)

    def answer(self) -> Text:
        return Text.assemble(
            self.message.copy(), " ", (self.answer_summary(), "richer_prompt.cursor")
        )

    def answer_summary(self) -> str:
        """The submitted choice as display text, for a Form review summary."""
        return (self.selected or self.current).display

    def result(self) -> T:
        return (self.selected or self.current).value


class Select(ChoicePrompt[T, T]):
    """
    Select a single choice from a vertical list.

    .. snapshot::
        :hide-code:

        Select.ask("Choose a color:", ["Red", "Green", "Blue"])

    Parameters
    ----------
    message: str or rich.text.Text
        The message to display above the choices.
    choices: iterable of T or Choice[T]
        The values to choose from.
        Each choice can be a raw value or an instance of :py:class:`Choice`,
        which allows customization of labels and descriptions.
    cursor_pointer: str, default "❯"
        The string to use as the cursor pointer.
    numbered: bool or None, default None
        Whether to display numbered choices, also enabling digit shortcuts (1-9).
        If `None`, show numbers only when there are at most 9 choices
        and they all fit in the viewport.

        .. versionchanged:: 0.2.0
            Numbers were previously shown by default.
    viewport_size: int or None, default None
        The maximum number of choices visible at once, at least 3.
        If `None`, fit as many choices as the terminal height allows.

        .. versionadded:: 0.2.0
    show_hint: bool, default True
        Whether to show a hint about how to select choices.
    console: rich.console.Console, optional
        A ``Console`` instance.
        If None, use the global console.

    Examples
    --------
    >>> prompt = Select("Choose a color:", ["Red", "Green", "Blue"])
    >>> color = prompt()
    """

    def __init__(
        self,
        message: TextType,
        choices: Iterable[Choice[T] | T],
        *,
        cursor_pointer: str = RIGHT_POINTER,
        numbered: bool | None = None,
        viewport_size: int | None = None,
        show_hint: bool = True,
        console: Console | None = None,
    ):
        super().__init__(message, choices, console=console)

        self.cursor_pointer = cursor_pointer
        self.numbered = numbered
        self.viewport_size = viewport_size
        self.show_hint = show_hint

    @classmethod
    def ask(
        cls,
        message: TextType,
        choices: Iterable[Choice[T] | T],
        *,
        index: int = 0,
        cursor_pointer: str = RIGHT_POINTER,
        numbered: bool | None = None,
        viewport_size: int | None = None,
        show_hint: bool = True,
        console: Console | None = None,
    ) -> T:
        """
        Shortcut to construct and run a prompt loop and return the result.

        Parameters
        ----------
        message: str or rich.text.Text
            The message to display above the choices.
        choices: iterable of T or Choice[T]
            The values to choose from.
            Each choice can be a raw value or an instance of :py:class:`Choice`,
            which allows customization of labels and descriptions.
        index: int, default 0
            The index of the choice to have the cursor start on.
        cursor_pointer: str, default "❯"
            The string to use as the cursor pointer.
        numbered: bool or None, default None
            Whether to display numbered choices, also enabling digit shortcuts (1-9).
            If `None`, show numbers only when there are at most 9 choices
            and they all fit in the viewport.

            .. versionchanged:: 0.2.0
                Numbers were previously shown by default.
        viewport_size: int or None, default None
            The maximum number of choices visible at once, at least 3.
            If `None`, fit as many choices as the terminal height allows.

            .. versionadded:: 0.2.0
        show_hint: bool, default True
            Whether to show a hint about how to select choices.
        console: rich.console.Console, optional
            A ``Console`` instance.
            If None, use the global console.

        Returns
        -------
        The value of the selected choice.

        Examples
        --------
        >>> color = Select.ask("Choose a color:", ["Red", "Green", "Blue"])
        """
        return cls(
            message,
            choices,
            cursor_pointer=cursor_pointer,
            numbered=numbered,
            show_hint=show_hint,
            viewport_size=viewport_size,
            console=console,
        )(index=index)

    def __call__(self, index: int = 0) -> T:
        """
        Run the prompt loop.

        Parameters
        ----------
        index: int, default 0
            The index of the choice to select by default.

        Returns
        -------
        The value of the selected choice.
        """
        return super().__call__(index)

    def _build_widget(self, index: int = 0) -> SelectWidget[T]:
        """Build a fresh widget for one prompt run."""
        viewport_size = resolve_viewport_size(
            self.viewport_size, self.console, VIEWPORT_OVERHEAD
        )

        return SelectWidget(
            message=self.message,
            choices=self.choices,
            cursor=index,
            cursor_pointer=self.cursor_pointer,
            numbered=resolve_numbered(self.numbered, self.choices, viewport_size),
            viewport_size=viewport_size,
            show_hint=self.show_hint,
        )

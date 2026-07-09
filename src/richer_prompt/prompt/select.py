from collections.abc import Iterable
from typing import Generic, TypeVar

from rich import get_console
from rich.console import Console, Group
from rich.text import Text, TextType

from richer_prompt import keys
from richer_prompt.choices import Choice, ensure_choice
from richer_prompt.rendering import (
    DOWN_ARROW,
    RIGHT_POINTER,
    UP_ARROW,
    choice_label,
    ensure_text,
    format_hint,
    number_cell,
    pointer_cell,
    resolve_numbered,
    viewport_slice,
)
from richer_prompt.session import run

T = TypeVar("T")


class SelectWidget(Generic[T]):
    def __init__(
        self,
        choices: list[Choice[T]],
        cursor: int = 0,
        *,
        message: TextType,
        cursor_pointer: str = RIGHT_POINTER,
        numbered: bool | None = None,
        viewport_size: int | None = None,
        show_hint: bool = True,
    ):
        if cursor < 0 or cursor >= len(choices):
            raise ValueError(f"Index '{cursor}' is out of range")

        if viewport_size is not None and viewport_size < 3:
            raise ValueError(f"Viewport size '{viewport_size}' must be at least 3")

        self.choices = choices
        self.cursor = cursor
        self.message = ensure_text(message, default_style="richer_prompt.title")
        self.cursor_pointer = cursor_pointer
        self.numbered = resolve_numbered(numbered, choices, viewport_size)
        self.viewport_size = viewport_size
        self.show_hint = show_hint

        self._submitted = False

    @property
    def submitted(self) -> bool:
        return self._submitted

    @property
    def current(self) -> Choice[T]:
        return self.choices[self.cursor]

    def submit(self) -> None:
        self._submitted = True

    def move(self, delta: int) -> None:
        self.cursor = (self.cursor + delta) % len(self.choices)

    def handle_key(self, key: str) -> bool:
        match key:
            case keys.DOWN:
                self.move(1)
            case keys.UP:
                self.move(-1)
            case keys.ENTER:
                self.submit()
            case _ if self.numbered and key.isdecimal():
                n = int(key) - 1
                if 0 <= n < len(self.choices):
                    self.cursor = n
                    self.submit()
            case _:
                return False

        return True

    def render(self) -> Group:
        rows: list[Text] = []

        if self.message:
            rows.append(self.message)
            rows.append(Text())

        number_width = len(str(len(self.choices)))
        viewport = viewport_slice(len(self.choices), self.viewport_size, self.cursor)

        for i in viewport:
            is_focused = i == self.cursor
            pointer = pointer_cell(
                self.cursor_pointer, is_focused, i, viewport, len(self.choices)
            )

            rows.append(
                Text.assemble(
                    pointer,
                    " ",
                    number_cell(i, number_width) if self.numbered else Text(),
                    choice_label(self.choices[i], is_focused),
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
            self.message.copy(), " ", (self.current.display, "richer_prompt.cursor")
        )

    def result(self) -> T:
        return self.current.value


class Select(Generic[T]):
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
        Whether to display numbered choices.
        If `None`, numbers are shown only when there are at most 9 choices and they
        all fit in the viewport, so every displayed number works as a digit shortcut.
        `True` always shows numbers (digit shortcuts still only reach choices 1-9);
        `False` never shows them and disables digit shortcuts.

        .. versionchanged:: 0.2.0
            The default behavior changed from always showing numbers to only showing
            them when there are at most 9 choices.
    viewport_size: int or None, default None
        The maximum number of choices visible at once, at least 3
        (the cursor row plus one row of context on each side).
        Longer lists scroll to keep the cursor centered,
        and dimmed ↑/↓ arrows on the edge rows mark hidden choices.
        If `None`, all choices are shown.

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
        self.choices: list[Choice[T]] = [ensure_choice(choice) for choice in choices]
        if not self.choices:
            raise ValueError("choices cannot be empty")

        self.message = message
        self.cursor_pointer = cursor_pointer
        self.numbered = numbered
        self.viewport_size = viewport_size
        self.show_hint = show_hint
        self.console = console or get_console()

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
            Whether to display numbered choices.
            If `None`, numbers are shown only when there are at most 9 choices and they
            all fit in the viewport, so every displayed number works as a digit shortcut.
            `True` always shows numbers (digit shortcuts still only reach choices 1-9);
            `False` never shows them and disables digit shortcuts.

            .. versionchanged:: 0.2.0
                The default behavior changed from always showing numbers to only showing
                them when there are at most 9 choices.
        viewport_size: int or None, default None
            The maximum number of choices visible at once, at least 3
            (the cursor row plus one row of context on each side).
            Longer lists scroll to keep the cursor centered,
            and dimmed ↑/↓ arrows on the edge rows mark hidden choices.
            If `None`, all choices are shown.

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
        widget = self._build_widget(index)

        self.pre_prompt()

        return run(widget, self.console)

    def _build_widget(self, index: int = 0) -> SelectWidget[T]:
        """Build a fresh widget for one prompt run."""
        return SelectWidget(
            self.choices,
            cursor=index,
            message=self.message,
            cursor_pointer=self.cursor_pointer,
            numbered=self.numbered,
            viewport_size=self.viewport_size,
            show_hint=self.show_hint,
        )

    def pre_prompt(self) -> None:
        """Hook to display something before the prompt."""

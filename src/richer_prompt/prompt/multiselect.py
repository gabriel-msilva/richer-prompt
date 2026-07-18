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
    checkbox_cell,
    choice_label,
    cursor_cell,
    format_hint,
    number_cell,
    pointer_cell,
    resolve_numbered,
    resolve_viewport_size,
    viewport_slice,
)
from richer_prompt.session import CONSUMED, IGNORED, Done, KeyOutcome

T = TypeVar("T")

# Rows rendered around the choices: message, blank lines, Submit, hint, and a margin line
VIEWPORT_OVERHEAD: Final = 6


@dataclasses.dataclass(slots=True)
class MultiSelectWidget(Generic[T]):
    message: Text
    choices: list[Choice[T]]
    cursor: int
    checked: set[int]
    cursor_pointer: str
    numbered: bool
    viewport_size: int
    show_hint: bool

    # Set once the Submit row is chosen, so an intentionally empty selection
    # still counts as an answer. A non-empty ``checked`` counts on its own.
    _submitted: bool = dataclasses.field(init=False, default=False)

    def __post_init__(self):
        # may point to the submit button
        if self.cursor < 0 or self.cursor > len(self.choices):
            raise ValueError(f"Index '{self.cursor}' is out of range")

        offenders = [x for x in self.checked if x < 0 or x >= len(self.choices)]
        if offenders:
            raise ValueError(f"Default indices {sorted(offenders)!r} are out of range")

        if self.viewport_size < 3:
            raise ValueError(f"Viewport size '{self.viewport_size}' must be at least 3")

    @property
    def answered(self) -> bool:
        # A checked box is itself an explicit choice, so the step counts as
        # answered as soon as anything is checked; pressing Submit also records
        # an intentionally empty selection.
        return self._submitted or bool(self.checked)

    @property
    def selected_choices(self) -> list[Choice[T]]:
        return [self.choices[i] for i in sorted(self.checked)]

    def submit(self) -> None:
        """Record that the Submit row was chosen."""
        self._submitted = True

    def move(self, delta: int) -> None:
        total_rows = len(self.choices) + 1
        self.cursor = (self.cursor + delta) % total_rows

    def toggle(self) -> None:
        if self.choices[self.cursor].disabled:
            return

        if self.cursor in self.checked:
            self.checked.remove(self.cursor)
        else:
            self.checked.add(self.cursor)

    def is_on_submit(self) -> bool:
        return self.cursor == len(self.choices)

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
                self.cursor = len(self.choices)  # the Submit row
            case keys.ENTER if self.is_on_submit():
                self.submit()
                return Done(self.result())
            case keys.ENTER | keys.SPACE if not self.is_on_submit():
                self.toggle()
            case _ if self.numbered and key.isdecimal():
                n = int(key) - 1
                if 0 <= n < len(self.choices) and not self.choices[n].disabled:
                    self.cursor = n
                    self.toggle()
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
            pointer = pointer_cell(
                self.cursor_pointer, is_focused, i, viewport, len(self.choices)
            )

            rows.append(
                Text.assemble(
                    pointer,
                    " ",
                    number_cell(i, number_width) if self.numbered else Text(),
                    checkbox_cell(i in self.checked, self.choices[i].disabled),
                    " ",
                    choice_label(self.choices[i], is_focused),
                )
            )

        submit_label = Text(
            "Submit",
            style="richer_prompt.cursor"
            if self.is_on_submit()
            else "richer_prompt.choice",
        )
        padding = " " * (number_width + 2) if self.numbered else ""

        rows.append(
            Text.assemble(
                cursor_cell(self.cursor_pointer, self.is_on_submit()),
                " ",
                padding,
                submit_label,
            )
        )

        if self.show_hint:
            rows.append(Text())
            rows.append(
                format_hint(
                    f"{UP_ARROW}{DOWN_ARROW} to navigate",
                    "Enter to select",
                    "Submit to finish",
                )
            )

        return Group(*rows)

    def answer(self) -> Text:
        values = self.answer_summary()
        if values:
            return Text.assemble(
                self.message.copy(), " ", (values, "richer_prompt.cursor")
            )

        return Text.assemble(
            self.message.copy(), " ", ("(none)", "richer_prompt.description")
        )

    def answer_summary(self) -> str:
        """The submitted choices as display text, for a Form review summary."""
        return ", ".join(choice.display for choice in self.selected_choices)

    def result(self) -> list[T]:
        return [choice.value for choice in self.selected_choices]


class MultiSelect(ChoicePrompt[T, list[T]]):
    """
    Select multiple choices from a vertical list.

    .. snapshot::
        :hide-code:

        MultiSelect.ask("Choose colors:", ["Red", "Green", "Blue"])

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
    show_hint: bool, default True
        Whether to show a hint about how to select choices.
    viewport_size: int or None, default None
        The maximum number of choices visible at once, at least 3.
        If `None`, fit as many choices as the terminal height allows.

        .. versionadded:: 0.2.0
    console: rich.console.Console, optional
        A ``Console`` instance.
        If None, use the global console.

    Examples
    --------
    >>> prompt = MultiSelect("Choose colors:", ["Red", "Green", "Blue"])
    >>> colors = prompt()
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
        default: set[int] | None = None,
        cursor_pointer: str = RIGHT_POINTER,
        numbered: bool | None = None,
        viewport_size: int | None = None,
        show_hint: bool = True,
        console: Console | None = None,
    ) -> list[T]:
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
        default: set of int, optional
            A set of indices of choices that should be selected by default.
        cursor_pointer: str, default "❯"
            The string to use as the cursor pointer.
        numbered: bool or None, default None
            Whether to display numbered choices, also enabling digit shortcuts (1-9).
            If `None`, show numbers only when there are at most 9 choices
            and they all fit in the viewport.

            .. versionchanged:: 0.2.0
                Numbers were previously shown by default.
        show_hint: bool, default True
            Whether to show a hint about how to select choices.
        viewport_size: int or None, default None
            The maximum number of choices visible at once, at least 3.
            If `None`, fit as many choices as the terminal height allows.

            .. versionadded:: 0.2.0
        console: rich.console.Console, optional
            A ``Console`` instance.
            If None, use the global console.

        Returns
        -------
        List of values of the selected choices.

        Examples
        --------
        >>> colors = MultiSelect.ask("Choose colors:", ["Red", "Green", "Blue"])
        """
        return cls(
            message,
            choices,
            cursor_pointer=cursor_pointer,
            numbered=numbered,
            viewport_size=viewport_size,
            show_hint=show_hint,
            console=console,
        )(index=index, default=default)

    def __call__(self, index: int = 0, default: set[int] | None = None) -> list[T]:
        """
        Run the prompt loop.

        Parameters
        ----------
        index: int, default 0
            The index of the choice to have the cursor start on.
        default: set of int, optional
            A set of indices of choices that should be selected by default.

        Returns
        -------
        List of values of the selected choices.
        """
        return super().__call__(index, default)

    def _build_widget(
        self, index: int = 0, default: set[int] | None = None
    ) -> MultiSelectWidget[T]:
        """Build a fresh widget for one prompt run."""
        viewport_size = resolve_viewport_size(
            self.viewport_size, self.console, VIEWPORT_OVERHEAD
        )

        return MultiSelectWidget(
            message=self.message,
            choices=self.choices,
            cursor=index,
            checked=set(default or []),
            cursor_pointer=self.cursor_pointer,
            numbered=resolve_numbered(self.numbered, self.choices, viewport_size),
            viewport_size=viewport_size,
            show_hint=self.show_hint,
        )

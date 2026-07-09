from collections.abc import Iterable
from typing import Generic, TypeVar

from rich.console import Console, Group
from rich.text import Text, TextType

from richer_prompt import keys
from richer_prompt.choices import Choice
from richer_prompt.prompt.base import ChoicePrompt
from richer_prompt.rendering import (
    LEFT_ARROW,
    RIGHT_ARROW,
    arrow_cell,
    ensure_text,
    tab_cell,
)

T = TypeVar("T")


class TabsWidget(Generic[T]):
    def __init__(
        self,
        choices: list[Choice[T]],
        cursor: int = 0,
        *,
        message: TextType,
    ):
        if cursor < 0 or cursor >= len(choices):
            raise ValueError(f"Index '{cursor}' is out of range")

        self.choices = choices
        self.cursor = cursor
        self.message = ensure_text(message, default_style="richer_prompt.title")
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
        cursor = self.cursor + delta

        self.cursor = max(0, min(len(self.choices) - 1, cursor))

    def handle_key(self, key: str) -> bool:
        key = keys.vim_motion(key)

        match key:
            case keys.RIGHT | keys.TAB:
                self.move(1)
            case keys.LEFT | keys.SHIFT_TAB:
                self.move(-1)
            case keys.ENTER:
                self.submit()
            case _:
                return False

        return True

    def render(self) -> Group:
        rows: list[Text] = []

        if self.message:
            rows.append(self.message)
            rows.append(Text())

        cells = [arrow_cell(LEFT_ARROW, self.cursor == 0)]
        cells.extend(
            tab_cell(choice, i == self.cursor) for i, choice in enumerate(self.choices)
        )
        cells.append(arrow_cell(RIGHT_ARROW, self.cursor == len(self.choices) - 1))

        rows.append(Text(" ").join(cells))
        rows.append(Text(self.current.description, style="richer_prompt.description"))

        return Group(*rows)

    def answer(self) -> Text:
        return Text.assemble(
            self.message.copy(), " ", (self.current.display, "richer_prompt.cursor")
        )

    def result(self) -> T:
        return self.current.value


class Tabs(ChoicePrompt[T, T]):
    """
    Select a single choice from a horizontal list.

    .. snapshot::
        :hide-code:

        Tabs.ask("Choose a color:", ["Red", "Green", "Blue"])

    Parameters
    ----------
    message: str or rich.text.Text
        The message to display above the choices.
    choices: iterable of T or Choice[T]
        The values to choose from.
        Each choice can be a raw value or an instance of :py:class:`Choice`,
        which allows customization of labels and descriptions.
    console: rich.console.Console, optional
        A ``Console`` instance.
        If None, use the global console.

    Examples
    --------
    >>> prompt = Tabs("Choose a color:", ["Red", "Green", "Blue"])
    >>> color = prompt()
    """

    @classmethod
    def ask(
        cls,
        message: TextType,
        choices: Iterable[Choice[T] | T],
        *,
        index: int = 0,
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
        console: rich.console.Console, optional
            A ``Console`` instance.
            If None, use the global console.

        Returns
        -------
        The value of the selected choice.

        Examples
        --------
        >>> color = Tabs.ask("Choose a color:", ["Red", "Green", "Blue"])
        """
        return cls(message, choices, console=console)(index=index)

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

    def _build_widget(self, index: int = 0) -> TabsWidget[T]:
        """Build a fresh widget for one prompt run."""
        return TabsWidget(
            self.choices,
            cursor=index,
            message=self.message,
        )

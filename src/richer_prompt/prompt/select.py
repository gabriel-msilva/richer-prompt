from collections.abc import Iterable
from typing import Generic, TypeVar

from rich import get_console
from rich.console import Console
from rich.text import TextType

from richer_prompt.choices import Choice, ensure_choice
from richer_prompt.models import SingleSelectionModel
from richer_prompt.renderers import RIGHT_POINTER, SingleSelectRenderer
from richer_prompt.session import SingleSelectSession

T = TypeVar("T")


class Select(Generic[T]):
    """
    Select a single choice from a vertical list.

    Parameters
    ----------
    message: str or rich.text.Text
        The message to display above the choices.
    choices: iterable of T or Choice[T]
        The values to choose from.
        Each choice can be a raw value or an instance of :py:class:`Choice`,
        which allows customization of labels and descriptions.
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
        numbered: bool = True,
        show_hint: bool = True,
        console: Console | None = None,
    ):
        self.choices: list[Choice[T]] = [ensure_choice(choice) for choice in choices]
        if not self.choices:
            raise ValueError("choices cannot be empty")

        self.renderer = SingleSelectRenderer(
            message,
            cursor_pointer=cursor_pointer,
            numbered=numbered,
            show_hint=show_hint,
        )

        self.console = console or get_console()

    @classmethod
    def ask(
        cls,
        message: TextType,
        choices: Iterable[T],
        *,
        index: int = 0,
        cursor_pointer: str = RIGHT_POINTER,
        numbered: bool = True,
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
        numbered: bool, default True
            Whether to display numbers next to the choices.
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
        session = SingleSelectSession(
            model=SingleSelectionModel(self.choices, cursor=index),
            renderer=self.renderer,
            console=self.console,
        )

        self.pre_prompt()

        return session.run()

    def pre_prompt(self) -> None:
        """Hook to display something before the prompt."""

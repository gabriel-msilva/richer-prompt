from collections.abc import Iterable
from typing import Generic, TypeVar

from rich import get_console
from rich.console import Console
from rich.text import TextType

from richer_prompt.choices import Choice, ensure_choice
from richer_prompt.models import MultiSelectionModel
from richer_prompt.renderers import RIGHT_POINTER, MultiSelectRenderer
from richer_prompt.session import MultiSelectSession

T = TypeVar("T")


class MultiSelect(Generic[T]):
    """
    Select multiple choices from a vertical list.

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
    numbered: bool, default True
        Whether to display numbers next to the choices.
    show_hint: bool, default True
        Whether to show a hint about how to select choices.
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
        numbered: bool = True,
        show_hint: bool = True,
        console: Console | None = None,
    ):
        self.message = message
        self.choices: list[Choice[T]] = [ensure_choice(choice) for choice in choices]

        if not self.choices:
            raise ValueError("choices cannot be empty")

        self.console = console or get_console()

        self.renderer = MultiSelectRenderer(
            message,
            cursor_pointer=cursor_pointer,
            numbered=numbered,
            show_hint=show_hint,
        )

    @classmethod
    def ask(
        cls,
        message: TextType,
        choices: Iterable[Choice[T] | T],
        *,
        index: int = 0,
        default: set[int] | None = None,
        cursor_pointer: str = RIGHT_POINTER,
        numbered: bool = True,
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
        numbered: bool, default True
            Whether to display numbers next to the choices.
        show_hint: bool, default True
            Whether to show a hint about how to select choices.
        console: rich.console.Console, optional
            A ``Console`` instance.
            If None, use the global console.

        Examples
        --------
        >>> colors = MultiSelect.ask("Choose colors:", ["Red", "Green", "Blue"])
        """
        return cls(
            message,
            choices,
            cursor_pointer=cursor_pointer,
            numbered=numbered,
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
        """

        default = default or set()

        session = MultiSelectSession(
            model=MultiSelectionModel(
                self.choices, cursor=index, selected=set(default)
            ),
            renderer=self.renderer,
            console=self.console,
        )

        self.pre_prompt()

        return session.run()

    def pre_prompt(self) -> None:
        """Hook to display something before the prompt."""

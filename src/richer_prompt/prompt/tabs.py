from collections.abc import Iterable
from typing import Generic, TypeVar

from rich import get_console
from rich.console import Console
from rich.text import TextType

from richer_prompt.models import TabsSelectionModel
from richer_prompt.options import Option, ensure_option
from richer_prompt.renderers import TabsRenderer
from richer_prompt.session import TabsSelectSession

T = TypeVar("T")


class Tabs(Generic[T]):
    """
    Select a single option from a horizontal list.

    Parameters
    ----------
    message: str or rich.text.Text
        The message to display above the options.
    options: iterable of T or Option[T]
        The values to choose from.
        Each option can be a raw value or an instance of `Option`,
        which allows customization of labels and descriptions.
    console: rich.console.Console, optional
        A ``Console`` instance.
        If None, use the global console.

    Examples
    --------
    >>> prompt = Tabs("Choose a color:", ["Red", "Green", "Blue"])
    >>> color = prompt()
    """

    def __init__(
        self,
        message: TextType,
        options: Iterable[Option[T] | T],
        *,
        console: Console | None = None,
    ):
        self.options: list[Option[T]] = [ensure_option(option) for option in options]
        if not self.options:
            raise ValueError("options cannot be empty")

        self.renderer = TabsRenderer(message)
        self.console = console or get_console()

    @classmethod
    def ask(
        cls,
        message: TextType,
        options: Iterable[T],
        *,
        index: int = 0,
        console: Console | None = None,
    ) -> T:
        """
        Shortcut to construct and run a prompt loop and return the result.

        Parameters
        ----------
        message: str or rich.text.Text
            The message to display above the options.
        options: iterable of T or Option[T]
            The values to choose from.
            Each option can be a raw value or an instance of `Option`,
            which allows customization of labels and descriptions.
        index: int, default 0
            The index of the option to have the cursor start on.
        console: rich.console.Console, optional
            A ``Console`` instance.
            If None, use the global console.

        Examples
        --------
        >>> color = Tabs.ask("Choose a color:", ["Red", "Green", "Blue"])
        """
        return cls(
            message,
            options,
            console=console,
        )(index=index)

    def __call__(self, index: int = 0) -> T:
        """
        Run the prompt loop.

        Parameters
        ----------
        index: int, default 0
            The index of the option to select by default.
        """
        session = TabsSelectSession(
            model=TabsSelectionModel(self.options, cursor=index),
            renderer=self.renderer,
            console=self.console,
        )

        self.pre_prompt()

        return session.run()

    def pre_prompt(self) -> None:
        """Hook to display something before the prompt."""

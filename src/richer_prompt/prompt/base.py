from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, Generic, TypeVar

from rich import get_console
from rich.console import Console
from rich.text import TextType

from richer_prompt.choices import Choice, ensure_choice
from richer_prompt.rendering import ensure_text
from richer_prompt.session import Widget, run

T = TypeVar("T")
R_co = TypeVar("R_co", covariant=True)


class ChoicePrompt(ABC, Generic[T, R_co]):
    """
    Base class for prompts that pick from a list of choices.

    Generic over ``T``, the choice value type, and ``R_co``, the prompt result type.

    Each run builds a new instance of :py:class:`~richer_prompt.session.Widget` via
    :py:meth:`_build_widget` and drives it in a :py:func:`~richer_prompt.session.run` loop.

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
    """

    def __init__(
        self,
        message: TextType,
        choices: Iterable[Choice[T] | T],
        *,
        console: Console | None = None,
    ):
        self.message = ensure_text(message, default_style="richer_prompt.title")

        self.choices: list[Choice[T]] = [ensure_choice(choice) for choice in choices]
        if not self.choices:
            raise ValueError("choices cannot be empty")

        self.console = console or get_console()

    @classmethod
    @abstractmethod
    def ask(
        cls,
        message: TextType,
        choices: Iterable[Choice[T] | T],
        *,
        console: Console | None = None,
    ) -> R_co:
        """Shortcut to construct and run a prompt loop and return the result."""

    def __call__(self, *args: Any, **kwargs: Any) -> R_co:
        """Run the prompt loop, forwarding all arguments to :py:meth:`_build_widget`."""
        widget = self._build_widget(*args, **kwargs)

        self.pre_prompt()

        return run(widget, self.console)

    @abstractmethod
    def _build_widget(self, *args: Any, **kwargs: Any) -> Widget[R_co]:
        """Build a fresh widget for one prompt run."""

    def pre_prompt(self) -> None:
        """Hook to display something before the prompt."""

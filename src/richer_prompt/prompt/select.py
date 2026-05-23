from collections.abc import Iterable
from typing import Generic, TypeVar

from rich import get_console
from rich.console import Console
from rich.text import TextType

from richer_prompt.models import SingleSelectionModel
from richer_prompt.options import Option, ensure_option
from richer_prompt.renderers import RIGHT_POINTER, SingleSelectRenderer
from richer_prompt.session import SingleSelectSession

T = TypeVar("T")


class Select(Generic[T]):
    def __init__(
        self,
        message: TextType,
        options: Iterable[Option[T] | T],
        *,
        cursor_pointer: str = RIGHT_POINTER,
        numbered: bool = True,
        show_hint: bool = True,
        console: Console | None = None,
    ):
        self.options: list[Option[T]] = [ensure_option(option) for option in options]
        if not self.options:
            raise ValueError("options cannot be empty")

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
        options: Iterable[T],
        *,
        index: int = 0,
        cursor_pointer: str = RIGHT_POINTER,
        numbered: bool = True,
        show_hint: bool = True,
        console: Console | None = None,
    ) -> T:
        return cls(
            message,
            options,
            cursor_pointer=cursor_pointer,
            numbered=numbered,
            show_hint=show_hint,
            console=console,
        )(index=index)

    def __call__(self, index: int = 0) -> T:
        session = SingleSelectSession(
            model=SingleSelectionModel(self.options, cursor=index),
            renderer=self.renderer,
            console=self.console,
        )

        self.pre_prompt()

        return session.run()

    def pre_prompt(self) -> None:
        """Hook to display something before the prompt."""


if __name__ == "__main__":
    Select.ask("Choose a protein", ["Ham", "Chicken", "Tofu"])

    Select.ask(
        "Choose a bread",
        [
            Option("white", label="White", description="Soft and fluffy"),
            Option("whole_wheat", label="Whole wheat", description="Nutty and hearty"),
            Option("sourdough", label="Sourdough", description="Tangy and crusty"),
        ],
    )

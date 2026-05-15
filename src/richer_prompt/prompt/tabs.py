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
        return cls(
            message,
            options,
            console=console,
        )(index=index)

    def __call__(self, index: int = 0) -> T:
        session = TabsSelectSession(
            model=TabsSelectionModel(self.options, cursor=index),
            renderer=self.renderer,
            console=self.console,
        )

        self.pre_prompt()

        return session.run()

    def pre_prompt(self) -> None:
        """Hook to display something before the prompt."""


if __name__ == "__main__":
    Tabs.ask(
        "Game difficulty",
        [
            Option("Easy", description="Reduces enemy health and damage by 50%"),
            Option("Normal"),
            Option("Hard", description="Increases enemy health and damage by 50%"),
        ],
        index=1,
    )

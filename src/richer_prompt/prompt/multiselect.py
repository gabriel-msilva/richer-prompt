from collections.abc import Iterable
from typing import Generic, TypeVar

from rich import get_console
from rich.console import Console
from rich.text import TextType

from richer_prompt.models import MultiSelectionModel
from richer_prompt.options import Option, ensure_option
from richer_prompt.renderers import RIGHT_POINTER, MultiSelectRenderer
from richer_prompt.session import MultiSelectSession

T = TypeVar("T")


class MultiSelect(Generic[T]):
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
        self.message = message
        self.options: list[Option[T]] = [ensure_option(option) for option in options]

        if not self.options:
            raise ValueError("options cannot be empty")

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
        options: Iterable[Option[T] | T],
        *,
        index: int = 0,
        default: set[int] | None = None,
        cursor_pointer: str = RIGHT_POINTER,
        numbered: bool = True,
        show_hint: bool = True,
        console: Console | None = None,
    ) -> list[T]:
        return cls(
            message,
            options,
            cursor_pointer=cursor_pointer,
            numbered=numbered,
            show_hint=show_hint,
            console=console,
        )(index=index, default=default)

    def __call__(self, index: int = 0, default: set[int] | None = None) -> list[T]:
        default = default or set()

        session = MultiSelectSession(
            model=MultiSelectionModel(
                self.options, cursor=index, selected=set(default)
            ),
            renderer=self.renderer,
            console=self.console,
        )

        self.pre_prompt()

        return session.run()

    def pre_prompt(self) -> None:
        """Hook to display something before the prompt."""

import dataclasses
from typing import Generic, TypeVar

import readchar
from rich import get_console
from rich.console import Console
from rich.live import Live

from richer_prompt.models import (
    MultiSelectionModel,
    SelectionModel,
    SingleSelectionModel,
    TabsSelectionModel,
)
from richer_prompt.renderers import (
    MultiSelectRenderer,
    Renderer,
    SingleSelectRenderer,
    TabsRenderer,
)

T = TypeVar("T")


def loop(renderer: Renderer, model: SelectionModel, console: Console):
    with Live(
        renderer.render(model),
        console=console,
        refresh_per_second=30,
        transient=True,
    ) as live:
        while not model.submitted:
            model.handle_key(readchar.readkey())
            live.update(renderer.render(model))

    console.print(renderer.get_answer(model))

    return model


class InteractiveSession(Generic[T]):
    model: SelectionModel[T]
    renderer: Renderer
    console: Console

    def run(self):
        with Live(
            self.renderer.render(self.model),
            console=self.console,
            refresh_per_second=30,
            transient=True,
        ) as live:
            while not self.model.submitted:
                self.model.handle_key(readchar.readkey())
                live.update(self.renderer.render(self.model))

        self.console.print(self.renderer.get_answer(self.model))

        return self.result()

    def result(self) -> T:
        raise NotImplementedError


@dataclasses.dataclass(slots=True)
class SingleSelectSession(InteractiveSession[T]):
    model: SingleSelectionModel[T]
    renderer: SingleSelectRenderer
    console: Console = dataclasses.field(default_factory=get_console)

    def result(self) -> T:
        return self.model.current.value


@dataclasses.dataclass(slots=True)
class MultiSelectSession(InteractiveSession[list[T]]):
    model: MultiSelectionModel[T]
    renderer: MultiSelectRenderer
    console: Console = dataclasses.field(default_factory=get_console)

    def result(self) -> list[T]:
        return [option.value for option in self.model.selected_values]


@dataclasses.dataclass(slots=True)
class TabsSelectSession(InteractiveSession[T]):
    model: TabsSelectionModel[T]
    renderer: TabsRenderer
    console: Console = dataclasses.field(default_factory=get_console)

    def result(self) -> T:
        return self.model.current.value

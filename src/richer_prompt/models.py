import dataclasses
from typing import Generic, Protocol, TypeVar

import readchar

from richer_prompt.options import Option

T = TypeVar("T")


class SelectionModel(Protocol, Generic[T]):
    options: list[Option[T]]
    cursor: int
    submitted: bool

    def handle_key(self, key: str) -> None: ...


@dataclasses.dataclass(slots=True)
class SingleSelectionModel(SelectionModel[T]):
    options: list[Option[T]]
    cursor: int = 0
    submitted: bool = dataclasses.field(default=False, init=False)

    def __post_init__(self):
        if self.cursor < 0 or self.cursor >= len(self.options):
            raise ValueError(f"Index '{self.cursor}' is out of range")

    @property
    def current(self) -> Option[T]:
        return self.options[self.cursor]

    def submit(self) -> None:
        self.submitted = True

    def move(self, delta: int) -> None:
        self.cursor = (self.cursor + delta) % len(self.options)

    def handle_key(self, key: str) -> None:
        match key:
            case readchar.key.DOWN:
                self.move(1)
            case readchar.key.UP:
                self.move(-1)
            case readchar.key.ENTER:
                self.submit()
            case _ if key.isdigit():
                n = int(key) - 1
                if 0 <= n < len(self.options):
                    self.cursor = n
                    self.submit()


@dataclasses.dataclass(slots=True)
class MultiSelectionModel(SelectionModel[T]):
    options: list[Option[T]]
    cursor: int = 0
    selected: set[int] = dataclasses.field(default_factory=set)
    submitted: bool = dataclasses.field(default=False, init=False)

    def __post_init__(self):
        if self.cursor < 0 or self.cursor > len(
            self.options
        ):  # may point to the submit button
            raise ValueError(f"Index '{self.cursor}' is out of range")

        offenders = [x for x in self.selected if x < 0 or x >= len(self.options)]
        if offenders:
            raise ValueError(f"Default indices {sorted(offenders)!r} are out of range")

    @property
    def submit_index(self) -> int:
        return len(self.options)

    @property
    def selected_values(self) -> list[Option[T]]:
        return [self.options[i] for i in sorted(self.selected)]

    def submit(self):
        if self.cursor == self.submit_index:
            self.submitted = True

    def move(self, delta: int):
        total_rows = len(self.options) + 1
        self.cursor = (self.cursor + delta) % total_rows

    def toggle(self):
        if self.cursor in self.selected:
            self.selected.remove(self.cursor)
        else:
            self.selected.add(self.cursor)

    def handle_key(self, key: str) -> None:
        match key:
            case readchar.key.DOWN:
                self.move(1)
            case readchar.key.UP:
                self.move(-1)
            case readchar.key.ENTER if self.cursor == self.submit_index:
                self.submitted = True
            case readchar.key.ENTER | readchar.key.SPACE if (
                self.cursor != self.submit_index
            ):
                self.toggle()
            case _ if key.isdigit():
                n = int(key) - 1
                if 0 <= n < len(self.options):
                    self.cursor = n
                    self.toggle()

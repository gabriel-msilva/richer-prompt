from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import readchar

from richer_prompt.options import Option

T = TypeVar("T")


class SelectionModel(ABC, Generic[T]):
    def __init__(self, options: list[Option[T]], cursor: int = 0):
        if cursor < 0 or cursor >= len(options):
            raise ValueError(f"Index '{cursor}' is out of range")

        self.options = options
        self.cursor = cursor
        self._submitted = False

    @property
    def submitted(self) -> bool:
        return self._submitted

    def submit(self) -> None:
        self._submitted = True

    @abstractmethod
    def handle_key(self, key: str) -> None: ...


class SingleSelectionModel(SelectionModel[T]):
    @property
    def current(self) -> Option[T]:
        return self.options[self.cursor]

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


class MultiSelectionModel(SelectionModel[T]):
    def __init__(
        self,
        options: list[Option[T]],
        cursor: int = 0,
        selected: set[int] | None = None,
    ):
        selected = set(selected or [])

        # may point to the submit button
        if cursor < 0 or cursor > len(options):
            raise ValueError(f"Index '{cursor}' is out of range")

        offenders = [x for x in selected if x < 0 or x >= len(options)]
        if offenders:
            raise ValueError(f"Default indices {sorted(offenders)!r} are out of range")

        self.options = options
        self.cursor = cursor
        self.selected = set(selected)
        self._submitted = False

    @property
    def selected_values(self) -> list[Option[T]]:
        return [self.options[i] for i in sorted(self.selected)]

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
            case readchar.key.ENTER if self.is_on_submit():
                self.submit()
            case readchar.key.ENTER | readchar.key.SPACE if not self.is_on_submit():
                self.toggle()
            case _ if key.isdigit():
                n = int(key) - 1
                if 0 <= n < len(self.options):
                    self.cursor = n
                    self.toggle()

    def is_on_submit(self) -> bool:
        return self.cursor == len(self.options)


class TabsSelectionModel(SelectionModel[T]):
    @property
    def current(self) -> Option[T]:
        return self.options[self.cursor]

    def move(self, delta: int) -> None:
        cursor = self.cursor + delta
        cursor = max(0, min(len(self.options) - 1, cursor))

        self.cursor = cursor

    def handle_key(self, key: str) -> None:
        previous = {readchar.key.LEFT}
        if hasattr(readchar.key, "SHIFT_TAB"):
            previous.add(readchar.key.SHIFT_TAB)

        match key:
            case readchar.key.RIGHT | readchar.key.TAB:
                self.move(1)
            case k if k in previous:
                self.move(-1)
            case readchar.key.ENTER:
                self.submit()

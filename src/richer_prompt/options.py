from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Option(Generic[T]):
    value: T
    label: str = ""
    description: str = ""

    @property
    def display(self) -> str:
        return self.label or str(self.value)


def ensure_option(value: T | Option[T]) -> Option[T]:
    return value if isinstance(value, Option) else Option(value)

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Option(Generic[T]):
    """
    A selectable option used by prompt classes.

    Parameters
    ----------
    value: T
        The option value returned when selected.
    label: str, optional
        The label to display for the option.
        If not provided, the value is used as the label.
    description: str, optional
        Additional text to describe the option.
    """

    value: T
    label: str = ""
    description: str = ""

    @property
    def display(self) -> str:
        """Get the display string for the option."""
        return self.label or str(self.value)


def ensure_option(value: T | Option[T]) -> Option[T]:
    return value if isinstance(value, Option) else Option(value)

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Choice(Generic[T]):
    """
    A selectable choice used by prompt classes.

    Parameters
    ----------
    value: T
        The choice value returned when selected.
    label: str, optional
        The label to display for the choice.
        If not provided, the value is used as the label.
    description: str, optional
        Additional text to describe the choice.
    disabled: bool, default False
        If `True`, the choice cannot be selected or toggled.

        .. versionadded:: 0.3.0
    """

    value: T
    label: str = ""
    description: str = ""
    disabled: bool = False

    @property
    def display(self) -> str:
        """Get the display string for the choice."""
        return self.label or str(self.value)


def ensure_choice(value: T | Choice[T]) -> Choice[T]:
    return value if isinstance(value, Choice) else Choice(value)

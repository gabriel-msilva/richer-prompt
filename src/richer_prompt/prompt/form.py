import dataclasses
from collections.abc import Callable
from typing import Any

from rich import get_console
from rich.console import Console, Group, RenderableType
from rich.text import Text

from richer_prompt import keys
from richer_prompt.choices import Choice
from richer_prompt.prompt.multiselect import MultiSelect, MultiSelectWidget
from richer_prompt.prompt.select import Select, SelectWidget
from richer_prompt.rendering import (
    BALLOT_BOX,
    BALLOT_BOX_WITH_X,
    BLACK_CIRCLE,
    HEAVY_CHECK_MARK,
    LEFT_ARROW,
    RIGHT_ARROW,
    RIGHT_POINTER,
    WARNING_SIGN,
    arrow_cell,
    format_hint,
    label_cell,
)
from richer_prompt.session import run


@dataclasses.dataclass(slots=True)
class FormWidget:
    # Values are SelectWidget/MultiSelectWidget; typed loosely so callers may
    # reach the concrete widget attributes (cursor, checked, ...) either type has.
    steps: dict[str, Any]
    confirm: SelectWidget[bool]
    cursor: int

    # Hook invoked when the form is submitted; set by drivers such as run().
    on_submit: Callable[[], None] | None = dataclasses.field(default=None, init=False)

    def __post_init__(self):
        if self.cursor < 0 or self.cursor > len(self.steps):
            raise ValueError(f"Index '{self.cursor}' is out of range")

        for step in self.steps.values():
            step.on_submit = self._advance

        self.confirm.on_submit = self._confirm

    @property
    def on_review(self) -> bool:
        return self.cursor == len(self.steps)

    @property
    def focused_step(self) -> SelectWidget | MultiSelectWidget:
        return list(self.steps.values())[self.cursor]

    def move(self, delta: int) -> None:
        self.cursor = max(0, min(len(self.steps), self.cursor + delta))

    def _advance(self) -> None:
        self.move(1)

    def _confirm(self) -> None:
        if self.confirm.result():
            if self.on_submit is not None:
                self.on_submit()
        else:
            raise KeyboardInterrupt

    def _is_answered(self, step: SelectWidget | MultiSelectWidget) -> bool:
        # A MultiSelect counts as answered as soon as a choice is checked, so
        # toggling records the answer without confirming the Submit row.
        if isinstance(step, MultiSelectWidget):
            return step.submitted or bool(step.checked)

        return step.submitted

    def handle_key(self, key: str) -> bool:
        key = keys.vim_motion(key)

        match key:
            case keys.LEFT | keys.SHIFT_TAB:
                self.move(-1)
                return True
            case keys.RIGHT | keys.TAB:
                self.move(1)
                return True

        if not self.on_review:
            return self.focused_step.handle_key(key)

        return self.confirm.handle_key(key)

    def render(self) -> RenderableType:
        rows: list[RenderableType] = [self._render_tabs(), Text()]

        if self.on_review:
            rows.append(self._render_review())
        else:
            rows.append(self.focused_step.render())
            rows.append(Text())
            rows.append(format_hint("Tab/Arrow keys to navigate", "Enter to select"))

        return Group(*rows)

    def answer(self) -> Text:
        return Text()

    def result(self) -> dict[str, Any]:
        return {
            name: step.result()
            for name, step in self.steps.items()
            if self._is_answered(step)
        }

    def _render_tabs(self) -> Text:
        cells = [
            label_cell(
                f"{BALLOT_BOX_WITH_X if self._is_answered(step) else BALLOT_BOX} {name}",
                focused=i == self.cursor,
            )
            for i, (name, step) in enumerate(self.steps.items())
        ]
        cells.append(label_cell(f"{HEAVY_CHECK_MARK} Submit", focused=self.on_review))

        return Text.assemble(
            arrow_cell(LEFT_ARROW, self.cursor == 0),
            " ",
            *cells,
            " ",
            arrow_cell(RIGHT_ARROW, self.on_review),
        )

    def _render_review(self) -> Group:
        sections: list[RenderableType] = [
            Text("Review your answers", style="richer_prompt.title")
        ]

        if not all(self._is_answered(step) for step in self.steps.values()):
            sections.append(
                Text(
                    f"{WARNING_SIGN} You have not answered all questions",
                    style="richer_prompt.warning",
                )
            )

        answered = [step for step in self.steps.values() if self._is_answered(step)]
        if answered:
            sections.append(
                Group(*(row for step in answered for row in _summary(step)))
            )

        sections.append(self.confirm.render())

        return Group(*_join(sections))


def _summary(step: SelectWidget | MultiSelectWidget) -> tuple[Text, Text]:
    """The two rows describing a submitted step in the review."""
    message = step.message.copy()
    message.style = "richer_prompt.choice"

    return (
        Text.assemble(f"{BLACK_CIRCLE} ", message),
        Text.assemble(
            "  ", (f"{RIGHT_ARROW} {step.answer_summary()}", "richer_prompt.selected")
        ),
    )


def _join(sections: list[RenderableType]) -> list[RenderableType]:
    """Interleave blank lines between sections."""
    rows: list[RenderableType] = []
    for i, section in enumerate(sections):
        if i:
            rows.append(Text())
        rows.append(section)

    return rows


class Form:
    """
    Ask a sequence of choice prompts as a single, navigable form.

    .. versionadded:: 0.3.0

    Steps are shown one at a time with a tab bar to move between them, followed
    by a review step to submit all answers at once.
    Only answered (submitted) steps appear in the result.

    .. snapshot::
        :hide-code:

        Form.ask(
            {
                "Protein": Select("Choose a protein:", ["Ham", "Chicken", "Tofu"]),
                "Bread": Select("Choose a bread:", ["White", "Wheat", "Rye"]),
                "Toppings": MultiSelect("Any toppings?", ["Lettuce", "Tomato", "Onion", "Pickles"]),
            }
        )

    Parameters
    ----------
    steps: dict
        Steps to ask.
        The keys are the names in navigation tabs and in the return dict,
        while the values are the prompts to ask.
        Only :py:class:`Select` and :py:class:`MultiSelect` are supported.
    console: rich.console.Console, optional
        A ``Console`` instance.
        If None, use the global console.

    Examples
    --------
    >>> Form(
    ...     {
    ...         "Protein": Select("Choose a protein:", ["Ham", "Chicken", "Tofu"]),
    ...         "Bread": Select("Choose a bread:", ["White", "Wheat", "Rye"]),
    ...         "Toppings": MultiSelect("Any toppings?", ["Lettuce", "Tomato", "Onion", "Pickles"]),
    ...     }
    ... )
    >>> answers = form()
    """

    def __init__(
        self,
        steps: dict[str, Select | MultiSelect],
        *,
        console: Console | None = None,
    ):
        for name, step in steps.items():
            if not isinstance(step, (Select, MultiSelect)):
                raise TypeError(
                    f"Step '{name}' must be a Select or MultiSelect, got {type(step).__name__}"
                )

        self.steps = steps
        self.console = console or get_console()

    @classmethod
    def ask(
        cls,
        steps: dict[str, Select | MultiSelect],
        *,
        console: Console | None = None,
    ) -> dict[str, Any]:
        """
        Shortcut to construct, run a form and return the answers.

        Parameters
        ----------
        steps: dict of str to Select or MultiSelect
            The prompts to ask, keyed by the name used in the result.
        console: rich.console.Console, optional
            A ``Console`` instance.
            If None, use the global console.

        Returns
        -------
        A dict of step name as keys and answer as value, for each answered step.

        Examples
        --------
        >>> answers = Form.ask(
        ...     {
        ...         "Protein": Select("Choose a protein:", ["Ham", "Chicken", "Tofu"]),
        ...         "Bread": Select("Choose a bread:", ["White", "Wheat", "Rye"]),
        ...         "Toppings": MultiSelect("Any toppings?", ["Lettuce", "Tomato", "Onion", "Pickles"]),
        ...     }
        ... )
        """
        return cls(steps, console=console)()

    def __call__(self) -> dict[str, Any]:
        """
        Run the form loop.

        Returns
        -------
        A dict of step name as keys and answer as value, for each answered step.
        """
        return run(self._build_widget(), self.console)

    def _build_widget(self, index: int = 0) -> FormWidget:
        steps = {}
        for name, prompt in self.steps.items():
            widget = prompt._build_widget()
            widget.show_hint = False
            steps[name] = widget

        confirm: SelectWidget[bool] = SelectWidget(
            message=Text(
                "Ready to submit your answers?", style="richer_prompt.description"
            ),
            choices=[Choice(True, "Submit answers"), Choice(False, "Cancel")],
            cursor=0,
            cursor_pointer=RIGHT_POINTER,
            numbered=True,
            viewport_size=3,
            show_hint=False,
        )

        return FormWidget(steps=steps, confirm=confirm, cursor=index)

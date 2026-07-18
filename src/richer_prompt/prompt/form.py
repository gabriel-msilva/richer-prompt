import dataclasses
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
from richer_prompt.session import CANCELLED, CONSUMED, Done, KeyOutcome, run


@dataclasses.dataclass(slots=True)
class FormWidget:
    # Values are SelectWidget/MultiSelectWidget; typed loosely so callers may
    # reach the concrete widget attributes (cursor, checked, ...) either type has.
    steps: dict[str, Any]
    confirm: SelectWidget[bool]
    cursor: int
    required: bool

    def __post_init__(self):
        if self.cursor < 0 or self.cursor > len(self.steps):
            raise ValueError(f"Index '{self.cursor}' is out of range")

    @property
    def on_review(self) -> bool:
        return self.cursor == len(self.steps)

    @property
    def complete(self) -> bool:
        return all(step.answered for step in self.steps.values())

    @property
    def focused_step(self) -> SelectWidget | MultiSelectWidget:
        return list(self.steps.values())[self.cursor]

    def move(self, delta: int) -> None:
        self.cursor = max(0, min(len(self.steps), self.cursor + delta))

    def handle_key(self, key: str) -> KeyOutcome:
        key = keys.vim_motion(key)

        match key:
            case keys.LEFT | keys.SHIFT_TAB:
                self.move(-1)
                return CONSUMED
            case keys.RIGHT | keys.TAB:
                self.move(1)
                return CONSUMED

        if self.on_review:
            return self._handle_confirm(key)

        return self._handle_step(key)

    def _handle_step(self, key: str) -> KeyOutcome:
        outcome = self.focused_step.handle_key(key)

        # A step signals completion by returning Done (the step owns its own
        # answer); in a form that just advances to the next step rather than
        # ending the run, so the event is swallowed here.
        if isinstance(outcome, Done):
            self.move(1)
            return CONSUMED

        return outcome

    def _handle_confirm(self, key: str) -> KeyOutcome:
        # Submit is disabled while a required form is incomplete, so the confirm
        # can only ever commit True when submission is actually allowed.
        self._sync_submit()
        outcome = self.confirm.handle_key(key)

        if not isinstance(outcome, Done):
            return outcome

        return Done(self.result()) if outcome.value else CANCELLED

    def _sync_submit(self) -> None:
        """Disable the confirm's Submit option while a required form is incomplete."""
        submit = self.confirm.choices[0]
        disabled = self.required and not self.complete
        if submit.disabled != disabled:
            self.confirm.choices[0] = dataclasses.replace(submit, disabled=disabled)

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
            name: step.result() for name, step in self.steps.items() if step.answered
        }

    def _render_tabs(self) -> Text:
        cells = [
            label_cell(
                f"{BALLOT_BOX_WITH_X if step.answered else BALLOT_BOX} {name}",
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
        self._sync_submit()

        sections: list[RenderableType] = [
            Text("Review your answers", style="richer_prompt.title")
        ]

        if not self.complete:
            sections.append(
                Text(
                    f"{WARNING_SIGN} You have not answered all questions",
                    style="richer_prompt.warning",
                )
            )

        answered = [step for step in self.steps.values() if step.answered]
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

    summary = step.answer_summary()
    detail = (
        (f"{RIGHT_ARROW} {summary}", "richer_prompt.selected")
        if summary
        else (f"{RIGHT_ARROW} (none)", "richer_prompt.description")
    )

    return (
        Text.assemble(f"{BLACK_CIRCLE} ", message),
        Text.assemble("  ", detail),
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
    Choosing *Cancel* on the review step raises
    :py:exc:`~richer_prompt.PromptCancelled`.

    By default every step must be answered before the form can be submitted, so
    the result always has one entry per step. Pass ``required=False`` to allow
    submitting a partial form, in which case only answered steps appear in the
    result.

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
    required: bool, default True
        Whether every step must be answered before the form can be submitted.
        When False, the form may be submitted with unanswered steps, which are
        then omitted from the result.
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
        required: bool = True,
        console: Console | None = None,
    ):
        for name, step in steps.items():
            if not isinstance(step, (Select, MultiSelect)):
                raise TypeError(
                    f"Step '{name}' must be a Select or MultiSelect, got {type(step).__name__}"
                )

        self.steps = steps
        self.required = required
        self.console = console or get_console()

    @classmethod
    def ask(
        cls,
        steps: dict[str, Select | MultiSelect],
        *,
        required: bool = True,
        console: Console | None = None,
    ) -> dict[str, Any]:
        """
        Shortcut to construct, run a form and return the answers.

        Parameters
        ----------
        steps: dict of str to Select or MultiSelect
            The prompts to ask, keyed by the name used in the result.
        required: bool, default True
            Whether every step must be answered before the form can be
            submitted. When False, unanswered steps are omitted from the result.
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
        return cls(steps, required=required, console=console)()

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

        return FormWidget(
            steps=steps, confirm=confirm, cursor=index, required=self.required
        )

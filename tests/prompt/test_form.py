import pytest

from richer_prompt import PromptCancelled, keys
from richer_prompt.prompt import Form, MultiSelect, Select, Tabs
from richer_prompt.testing import simulate_keys
from tests.utils import assert_snapshot, assert_widget_snapshot


@pytest.fixture
def form(console) -> Form:
    return Form(
        {
            "Select": Select("Select an option:", ["a", "b", "c"], console=console),
            "MultiSelect": MultiSelect(
                "Select multiple options:", ["x", "y", "z"], console=console
            ),
        },
        console=console,
    )


@pytest.mark.parametrize(
    ("keys", "expected"),
    [
        (
            [
                # Select "a"
                keys.ENTER,
                # Select "x" and "z", submit
                keys.ENTER,
                keys.DOWN,
                keys.DOWN,
                keys.ENTER,
                keys.DOWN,
                keys.ENTER,
                # Submit form
                keys.ENTER,
            ],
            {"Select": "a", "MultiSelect": ["x", "z"]},
        ),
        (
            [keys.ENTER, keys.RIGHT, keys.ENTER],
            {"Select": "a"},
        ),
        (
            [keys.RIGHT, keys.RIGHT, keys.ENTER],
            {},
        ),
    ],
    ids=[
        "all steps",
        "partial steps",
        "no steps",
    ],
)
def test_that_choices_are_selected_and_submitted(form: Form, keys, expected):
    with simulate_keys(*keys):
        assert form() == expected


def test_that_tab_and_shift_tab_navigate_between_steps(form: Form):
    with simulate_keys(
        keys.TAB,
        keys.TAB,
        keys.SHIFT_TAB,
        keys.UP,
        keys.ENTER,
        keys.ENTER,
    ):
        assert form() == {"MultiSelect": []}


def test_that_vertical_navigation_is_forwarded_to_focused_step(form: Form):
    with simulate_keys(
        # Select: navigate to end, back to start, and select "a"
        keys.UP,
        keys.HOME,
        keys.ENTER,
        # MultiSelect: select "y", go to end, and submit
        keys.DOWN,
        keys.ENTER,
        keys.END,
        keys.ENTER,
        # submit form
        keys.ENTER,
    ):
        assert form() == {"Select": "a", "MultiSelect": ["y"]}


def test_that_vim_keys_navigate(form: Form):
    with simulate_keys(
        # go to "Submit" step
        "l",
        "l",
        # go back to "MultiSelect" step, toggle "y" and submit
        "h",
        "j",
        keys.ENTER,
        "k",
        "k",
        keys.ENTER,
        # submit form
        keys.ENTER,
    ):
        assert form() == {"MultiSelect": ["y"]}


def test_that_cancel_aborts_the_form(form: Form):
    with (
        simulate_keys(keys.RIGHT, keys.RIGHT, keys.DOWN, keys.ENTER),
        pytest.raises(PromptCancelled),
    ):
        form()


@pytest.mark.parametrize(
    ("keys", "expected"),
    [
        ([keys.LEFT, keys.ENTER, keys.RIGHT, keys.ENTER], {"Select": "a"}),
        ([keys.RIGHT, keys.RIGHT, keys.RIGHT, keys.ENTER], {}),
    ],
    ids=["left", "right"],
)
def test_that_steps_dont_rollover(form: Form, keys, expected):
    with simulate_keys(*keys):
        assert form() == expected


def test_that_runs_are_independent(form: Form):
    with simulate_keys(keys.ENTER, keys.RIGHT, keys.ENTER):
        assert form() == {"Select": "a"}

    with simulate_keys(keys.RIGHT, keys.RIGHT, keys.ENTER):
        assert form() == {}


def test_ask():
    steps = {
        "Select": Select("Select an option:", ["a", "b", "c"]),
        "MultiSelect": MultiSelect("Select multiple options:", ["x", "y", "z"]),
    }

    with simulate_keys(keys.ENTER, keys.UP, keys.ENTER, keys.ENTER):
        assert Form.ask(steps) == {"Select": "a", "MultiSelect": []}


@pytest.mark.parametrize("index", [-1, 3])
def test_that_index_out_of_range_raises(form: Form, index):
    with pytest.raises(ValueError, match=f"Index '{index}' is out of range"):
        form._build_widget(index=index)


def test_that_non_choice_steps_are_rejected(console):
    with pytest.raises(TypeError, match="Select or MultiSelect"):
        Form(
            {
                "Ok": Select("Select an option:", ["a", "b", "c"], console=console),
                "Bad": Tabs("Select an option:", ["a", "b", "c"], console=console),
            },  # ty:ignore[invalid-argument-type]
            console=console,
        )


def test_that_reselection_advances_to_next_step(form: Form):
    with simulate_keys(
        # Select: select "a"
        keys.ENTER,
        # go back to 'Select' and select "b"
        keys.LEFT,
        keys.DOWN,
        keys.ENTER,
        # go forward and submit
        keys.RIGHT,
        keys.ENTER,
    ):
        assert form() == {"Select": "b"}


def test_that_navigating_between_steps_does_not_update_previous_answers(form: Form):
    with simulate_keys(
        # select "a"
        keys.ENTER,
        # go back and navigate choices
        keys.LEFT,
        keys.DOWN,
        # go forward and submit
        keys.RIGHT,
        keys.RIGHT,
        keys.ENTER,
    ):
        assert form() == {"Select": "a"}


def test_that_toggling_a_multiselect_records_the_answer_without_submitting(form: Form):
    with simulate_keys(
        # MultiSelect: toggle "x", then leave via the tab bar without submitting
        keys.RIGHT,
        keys.ENTER,
        keys.RIGHT,
        # submit the form
        keys.ENTER,
    ):
        assert form() == {"MultiSelect": ["x"]}


def test_that_editing_a_submitted_multiselect_updates_the_answer(form: Form):
    with simulate_keys(
        # MultiSelect: select "x" and "z", then submit
        keys.RIGHT,
        keys.ENTER,
        keys.DOWN,
        keys.DOWN,
        keys.ENTER,
        keys.DOWN,
        keys.ENTER,
        # go back and untoggle "z"; toggling updates the answer without resubmitting
        keys.LEFT,
        keys.UP,
        keys.ENTER,
        # go forward and submit the form
        keys.RIGHT,
        keys.ENTER,
    ):
        assert form() == {"MultiSelect": ["x"]}


def test_that_each_step_is_rendered(form: Form):
    expected = """
    ←  ☐ Select  ☐ MultiSelect  ✔ Submit  →

    Select an option:

    ❯ 1. a
      2. b
      3. c

    Tab/Arrow keys to navigate · Enter to select
    """

    assert_snapshot(form, expected)

    expected = """
    ←  ☐ Select  ☐ MultiSelect  ✔ Submit  →

    Select multiple options:

    ❯ 1. [ ] x
      2. [ ] y
      3. [ ] z
         Submit

    Tab/Arrow keys to navigate · Enter to select
    """

    assert_snapshot(form, expected, index=1)

    expected = """
    ←  ☐ Select  ☐ MultiSelect  ✔ Submit  →

    Review your answers

    ⚠ You have not answered all questions

    Ready to submit your answers?

    ❯ 1. Submit answers
      2. Cancel
    """

    assert_snapshot(form, expected, index=2)


def test_that_partially_answered_select_step_shows_warning(form: Form):
    widget = form._build_widget(index=2)
    widget.steps["Select"].submit()

    expected = """
    ←  ☒ Select  ☐ MultiSelect  ✔ Submit  →

    Review your answers

    ⚠ You have not answered all questions

    ● Select an option:
      → a

    Ready to submit your answers?

    ❯ 1. Submit answers
      2. Cancel
    """

    assert_widget_snapshot(widget, expected)


def test_that_partially_answered_multiselect_step_shows_warning(form: Form):
    widget = form._build_widget(index=2)
    widget.steps["MultiSelect"].checked = {0, 2}
    widget.steps["MultiSelect"].submit()

    expected = """
    ←  ☐ Select  ☒ MultiSelect  ✔ Submit  →

    Review your answers

    ⚠ You have not answered all questions

    ● Select multiple options:
      → x, z

    Ready to submit your answers?

    ❯ 1. Submit answers
      2. Cancel
    """

    assert_widget_snapshot(widget, expected)


def test_that_fully_answered_form_does_not_show_warning(form: Form):
    widget = form._build_widget(index=2)
    widget.steps["Select"].submit()

    widget.steps["MultiSelect"].checked = {0, 2}
    widget.steps["MultiSelect"].submit()

    expected = """
    ←  ☒ Select  ☒ MultiSelect  ✔ Submit  →

    Review your answers

    ● Select an option:
      → a
    ● Select multiple options:
      → x, z

    Ready to submit your answers?

    ❯ 1. Submit answers
      2. Cancel
    """

    assert_widget_snapshot(widget, expected)


def test_style(form: Form):
    widget = form._build_widget(index=2)
    widget.steps["Select"].submit()

    expected = """
    ←  ☒ Select  ☐ MultiSelect [richer_prompt.tab.active] ✔ Submit [/] [richer_prompt.hint]→[/]

    [richer_prompt.title]Review your answers[/]

    [richer_prompt.warning]⚠ You have not answered all questions[/]

    ● [richer_prompt.choice]Select an option:[/]
      [richer_prompt.selected]→ a[/]

    [richer_prompt.description]Ready to submit your answers?[/]

    [richer_prompt.cursor]❯[/] [richer_prompt.description]1. [/][richer_prompt.cursor]Submit answers[/]
      [richer_prompt.description]2. [/][richer_prompt.choice]Cancel[/]
    """

    assert_widget_snapshot(widget, expected, raw=True)

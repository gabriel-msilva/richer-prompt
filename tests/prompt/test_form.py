import pytest

from richer_prompt import Choice, Form, MultiSelect, PromptCancelled, Select, Tabs, keys
from richer_prompt.testing import simulate_keys
from tests.utils import assert_snapshot, assert_widget_snapshot


@pytest.fixture
def form(console) -> Form:
    # The default form requires every step to be answered before submitting.
    return Form(
        {
            "Select": Select("Select an option:", ["a", "b", "c"], console=console),
            "MultiSelect": MultiSelect(
                "Select multiple options:", ["x", "y", "z"], console=console
            ),
        },
        console=console,
    )


@pytest.fixture
def optional_form(console) -> Form:
    # required=False allows submitting with unanswered steps omitted.
    return Form(
        {
            "Select": Select("Select an option:", ["a", "b", "c"], console=console),
            "MultiSelect": MultiSelect(
                "Select multiple options:", ["x", "y", "z"], console=console
            ),
        },
        required=False,
        console=console,
    )


def test_that_choices_are_selected_and_submitted(form: Form):
    with simulate_keys(
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
    ):
        assert form() == {"Select": "a", "MultiSelect": ["x", "z"]}


def test_that_labelled_choices_are_selected_and_submitted(console):
    form = Form(
        {
            "Select": Select(
                "Select an option:",
                [
                    Choice("a", label="Option A"),
                    Choice("b", label="Option B"),
                    Choice("c", label="Option C"),
                ],
                console=console,
            ),
            "MultiSelect": MultiSelect(
                "Select multiple options:",
                [
                    Choice("x", label="Option X"),
                    Choice("y", label="Option Y"),
                    Choice("z", label="Option Z"),
                ],
                console=console,
            ),
        },
        console=console,
    )

    with simulate_keys(
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
    ):
        assert form() == {"Select": "a", "MultiSelect": ["x", "z"]}


@pytest.mark.parametrize(
    ("keys", "expected"),
    [
        ([keys.ENTER, keys.RIGHT, keys.ENTER], {"Select": "a"}),
        ([keys.RIGHT, keys.RIGHT, keys.ENTER], {}),
    ],
    ids=["partial steps", "no steps"],
)
def test_that_an_optional_form_omits_unanswered_steps(
    optional_form: Form, keys, expected
):
    with simulate_keys(*keys):
        assert optional_form() == expected


def test_that_submit_is_blocked_until_all_steps_are_answered(form: Form):
    with simulate_keys(
        # answer only Select, then try to submit from the review
        keys.ENTER,
        keys.RIGHT,
        keys.ENTER,  # "Submit answers" is refused: MultiSelect is unanswered
        # go back, answer MultiSelect, then return and submit
        keys.LEFT,
        keys.ENTER,
        keys.RIGHT,
        keys.ENTER,
    ):
        assert form() == {"Select": "a", "MultiSelect": ["x"]}


def test_that_an_explicitly_empty_multiselect_counts_as_answered(form: Form):
    with simulate_keys(
        keys.ENTER,  # Select "a"
        keys.END,  # MultiSelect: jump to the Submit row
        keys.ENTER,  # submit with nothing checked; still counts as answered
        keys.ENTER,  # submit the form
    ):
        assert form() == {"Select": "a", "MultiSelect": []}


def test_that_cancel_aborts_the_form(form: Form):
    with (
        # Cancel is allowed even though no step has been answered.
        simulate_keys(keys.RIGHT, keys.RIGHT, keys.DOWN, keys.ENTER),
        pytest.raises(PromptCancelled),
    ):
        form()


def test_that_tab_and_shift_tab_navigate_between_steps(form: Form):
    with simulate_keys(
        # walk to the review with Tab, then back to the start with Shift+Tab
        keys.TAB,
        keys.TAB,
        keys.SHIFT_TAB,
        keys.SHIFT_TAB,
        # answer both steps and submit
        keys.ENTER,
        keys.UP,
        keys.ENTER,
        keys.ENTER,
    ):
        assert form() == {"Select": "a", "MultiSelect": []}


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
        # go right to the review, then left back to "Select"
        "l",
        "l",
        "h",
        "h",
        # select "a", then toggle "y" and submit
        keys.ENTER,
        "j",
        keys.ENTER,
        "k",
        "k",
        keys.ENTER,
        # submit form
        keys.ENTER,
    ):
        assert form() == {"Select": "a", "MultiSelect": ["y"]}


@pytest.mark.parametrize(
    ("key", "index", "expected"),
    [
        (keys.LEFT, 0, 0),
        (keys.RIGHT, 2, 2),
    ],
    ids=["left", "right"],
)
def test_that_steps_dont_rollover(form: Form, key, index, expected):
    widget = form._build_widget(index=index)
    widget.handle_key(key)

    assert widget.cursor == expected


def test_that_runs_are_independent(form: Form):
    with simulate_keys(keys.ENTER, keys.END, keys.ENTER, keys.ENTER):
        assert form() == {"Select": "a", "MultiSelect": []}

    with simulate_keys(keys.DOWN, keys.ENTER, keys.END, keys.ENTER, keys.ENTER):
        assert form() == {"Select": "b", "MultiSelect": []}


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
        # answer MultiSelect and submit
        keys.END,
        keys.ENTER,
        keys.ENTER,
    ):
        assert form() == {"Select": "b", "MultiSelect": []}


def test_that_navigating_between_steps_does_not_update_previous_answers(form: Form):
    with simulate_keys(
        # select "a"
        keys.ENTER,
        # go back and navigate choices without reselecting
        keys.LEFT,
        keys.DOWN,
        # go forward, answer MultiSelect and submit
        keys.RIGHT,
        keys.END,
        keys.ENTER,
        keys.ENTER,
    ):
        assert form() == {"Select": "a", "MultiSelect": []}


def test_that_toggling_a_multiselect_records_the_answer_without_submitting(form: Form):
    with simulate_keys(
        # Select "a"
        keys.ENTER,
        # MultiSelect: toggle "x", then leave via the tab bar without its Submit row
        keys.ENTER,
        keys.RIGHT,
        # submit the form
        keys.ENTER,
    ):
        assert form() == {"Select": "a", "MultiSelect": ["x"]}


def test_that_editing_a_submitted_multiselect_updates_the_answer(form: Form):
    with simulate_keys(
        # Select "a"
        keys.ENTER,
        # MultiSelect: select "x" and "z", then submit
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
        assert form() == {"Select": "a", "MultiSelect": ["x"]}


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


def test_that_no_selection_on_multiselect_counts_as_answered(form: Form):
    widget = form._build_widget(index=2)
    widget.steps["Select"].submit()

    widget.steps["MultiSelect"].checked = set()
    widget.steps["MultiSelect"].submit()

    expected = """
    ←  ☒ Select  ☒ MultiSelect  ✔ Submit  →

    Review your answers

    ● Select an option:
      → a
    ● Select multiple options:
      → (none)

    Ready to submit your answers?

    ❯ 1. Submit answers
      2. Cancel
    """

    assert_widget_snapshot(widget, expected)


def test_that_hint_is_hidden(form: Form):
    form.show_hint = False
    expected = """
    ←  ☐ Select  ☐ MultiSelect  ✔ Submit  →

    Select an option:

    ❯ 1. a
      2. b
      3. c
    """

    assert_snapshot(form, expected)


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

    [richer_prompt.cursor]❯[/] [richer_prompt.description]1. [/][richer_prompt.disabled]Submit answers[/]
      [richer_prompt.description]2. [/][richer_prompt.choice]Cancel[/]
    """

    assert_widget_snapshot(widget, expected, raw=True)

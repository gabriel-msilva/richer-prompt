import pytest
import readchar

from richer_prompt.choices import Choice
from richer_prompt.prompt.multiselect import MultiSelect
from richer_prompt.testing import simulate_keys
from tests.utils import assert_snapshot


@pytest.fixture
def multiselect(console) -> MultiSelect:
    return MultiSelect("Select multiple choices:", ["a", "b", "c"], console=console)


def test_that_choices_are_selected(multiselect: MultiSelect):
    keys = [
        readchar.key.ENTER,
        readchar.key.DOWN,
        readchar.key.DOWN,
        readchar.key.ENTER,
        readchar.key.DOWN,
        readchar.key.ENTER,
    ]

    with simulate_keys(keys):
        assert multiselect() == ["a", "c"]


def test_that_choices_can_be_unselected(multiselect: MultiSelect):
    keys = [
        readchar.key.ENTER,
        readchar.key.DOWN,
        readchar.key.ENTER,
        readchar.key.ENTER,
        readchar.key.DOWN,
        readchar.key.DOWN,
        readchar.key.ENTER,
    ]

    with simulate_keys(keys):
        assert multiselect() == ["a"]


def test_that_space_toggles(multiselect: MultiSelect):
    with simulate_keys([readchar.key.SPACE, readchar.key.UP, readchar.key.ENTER]):
        assert multiselect() == ["a"]


def test_that_space_toggle_on_submit_is_noop(multiselect: MultiSelect):
    with simulate_keys([readchar.key.UP, readchar.key.SPACE, readchar.key.ENTER]):
        assert multiselect() == []


def test_that_number_key_move_and_check(multiselect: MultiSelect):
    keys = ["0", "2", readchar.key.DOWN, readchar.key.DOWN, readchar.key.ENTER]

    with simulate_keys(keys):
        assert multiselect() == ["b"]


def test_that_number_key_out_of_range_is_ignored(multiselect: MultiSelect):
    with simulate_keys(["0", "4", readchar.key.UP, readchar.key.ENTER]):
        assert multiselect() == []


def test_rollover(multiselect: MultiSelect):
    keys = [
        readchar.key.UP,
        readchar.key.DOWN,
        readchar.key.ENTER,
        readchar.key.DOWN,
        readchar.key.DOWN,
        readchar.key.DOWN,
        readchar.key.ENTER,
    ]

    with simulate_keys(keys):
        assert multiselect() == ["a"]


def test_that_cursor_starts_at_index(multiselect: MultiSelect):
    with simulate_keys([readchar.key.ENTER, readchar.key.DOWN, readchar.key.ENTER]):
        assert multiselect(index=2) == ["c"]


def test_that_cursor_can_start_at_submit(multiselect: MultiSelect):
    with simulate_keys([readchar.key.ENTER]):
        assert multiselect(index=3) == []


@pytest.mark.parametrize("index", [-1, 4])
def test_that_index_out_of_range_raises(multiselect, index):
    with pytest.raises(ValueError, match=f"Index '{index}' is out of range"):
        multiselect(index=index)


@pytest.mark.parametrize(
    ("default", "expected"),
    [
        (None, []),
        ({1}, ["b"]),
        ({0, 2}, ["a", "c"]),
    ],
)
def test_that_default_is_prechecked(multiselect, default, expected):
    with simulate_keys([readchar.key.UP, readchar.key.ENTER]):
        assert multiselect(default=default) == expected


def test_that_default_indices_out_of_range_raises(multiselect):
    with pytest.raises(
        ValueError, match="Default indices \\[-1, 3\\] are out of range"
    ):
        multiselect(default={-1, 0, 1, 3})


def test_ask():
    with simulate_keys([readchar.key.ENTER, readchar.key.DOWN, readchar.key.ENTER]):
        assert MultiSelect.ask("Pick", ["a", "b", "c"], index=2) == ["c"]


def test_that_answer_is_not_affected_by_subsequent_calls(multiselect: MultiSelect):
    with simulate_keys([readchar.key.ENTER, readchar.key.UP, readchar.key.ENTER]):
        assert multiselect() == ["a"]

    keys = [
        readchar.key.DOWN,
        readchar.key.ENTER,
        readchar.key.DOWN,
        readchar.key.DOWN,
        readchar.key.ENTER,
    ]

    with simulate_keys(keys):
        assert multiselect() == ["b"]


def test_that_answer_is_rendered(multiselect: MultiSelect):
    keys = [
        readchar.key.ENTER,
        readchar.key.DOWN,
        readchar.key.DOWN,
        readchar.key.ENTER,
        readchar.key.DOWN,
        readchar.key.ENTER,
    ]

    with multiselect.console.capture() as capture, simulate_keys(keys):
        multiselect()

    assert capture.get() == "Select multiple choices: a, c\n"


def test_that_str_choices_are_rendered(multiselect: MultiSelect):
    widget = multiselect._build_widget()

    expected = """
    Select multiple choices:

    ❯ 1. [ ] a
      2. [ ] b
      3. [ ] c
         Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(widget, expected)


def test_that_labels_and_descriptions_are_rendered():
    prompt = MultiSelect(
        "Select multiple choices:",
        [
            Choice(value="a", label="Choice A"),
            Choice(value="b", description="The second choice"),
            Choice(value="c", label="Choice C", description="The third choice"),
        ],
    )

    widget = prompt._build_widget()

    expected = """
    Select multiple choices:

    ❯ 1. [ ] Choice A
      2. [ ] b  The second choice
      3. [ ] Choice C  The third choice
         Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(widget, expected)


def test_that_choices_are_rendered_without_numbers():
    prompt = MultiSelect("Select multiple choices:", ["a", "b", "c"], numbered=False)
    widget = prompt._build_widget()

    expected = """
    Select multiple choices:

    ❯ [ ] a
      [ ] b
      [ ] c
      Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(widget, expected)


def test_that_cursor_pointer_moves(multiselect: MultiSelect):
    widget = multiselect._build_widget(index=1)

    expected = """
    Select multiple choices:

      1. [ ] a
    ❯ 2. [ ] b
      3. [ ] c
         Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(widget, expected)


def test_that_checkbox_indicators_are_rendered(multiselect: MultiSelect):
    widget = multiselect._build_widget(default={0, 2})

    expected = """
    Select multiple choices:

    ❯ 1. [✓] a
      2. [ ] b
      3. [✓] c
         Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(widget, expected)


def test_custom_pointer():
    multiselect = MultiSelect(
        "Select multiple choices:", ["a", "b", "c"], cursor_pointer=">>"
    )
    widget = multiselect._build_widget()

    expected = """
    Select multiple choices:

    >> 1. [ ] a
       2. [ ] b
       3. [ ] c
          Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(widget, expected)


def test_that_hint_is_hidden():
    prompt = MultiSelect("Select multiple choices:", ["a", "b", "c"], show_hint=False)
    widget = prompt._build_widget()

    expected = """
    Select multiple choices:

    ❯ 1. [ ] a
      2. [ ] b
      3. [ ] c
         Submit
    """

    assert_snapshot(widget, expected)


def test_that_10_or_more_choices_are_aligned():
    prompt = MultiSelect(
        "Select multiple choices:", [f"Choice {i}" for i in range(1, 11)]
    )
    widget = prompt._build_widget()

    expected = """
    Select multiple choices:

    ❯  1. [ ] Choice 1
       2. [ ] Choice 2
       3. [ ] Choice 3
       4. [ ] Choice 4
       5. [ ] Choice 5
       6. [ ] Choice 6
       7. [ ] Choice 7
       8. [ ] Choice 8
       9. [ ] Choice 9
      10. [ ] Choice 10
          Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(widget, expected)


def test_style():
    prompt = MultiSelect(
        "Select multiple choices:",
        [
            Choice("a", description="The first choice"),
            Choice("b", description="The second choice"),
            Choice("c", description="The third choice"),
        ],
    )

    widget = prompt._build_widget(default={0})
    expected = """
    [richer_prompt.title]Select multiple choices:[/]

    [richer_prompt.cursor]❯[/] [richer_prompt.description]1. [/][richer_prompt.checkbox.checked][✓][/] [richer_prompt.cursor]a[/]  [richer_prompt.description]The first choice[/]
      [richer_prompt.description]2. [/][ ] b  [richer_prompt.description]The second choice[/]
      [richer_prompt.description]3. [/][ ] c  [richer_prompt.description]The third choice[/]
         Submit

    [richer_prompt.hint]↑↓ to navigate · Enter to select · Submit to finish[/]
    """

    assert_snapshot(widget, expected, raw=True)

    widget = prompt._build_widget(index=3)
    expected = """
    [richer_prompt.title]Select multiple choices:[/]

      [richer_prompt.description]1. [/][ ] a  [richer_prompt.description]The first choice[/]
      [richer_prompt.description]2. [/][ ] b  [richer_prompt.description]The second choice[/]
      [richer_prompt.description]3. [/][ ] c  [richer_prompt.description]The third choice[/]
    [richer_prompt.cursor]❯[/]    [richer_prompt.cursor]Submit[/]

    [richer_prompt.hint]↑↓ to navigate · Enter to select · Submit to finish[/]
    """

    assert_snapshot(widget, expected, raw=True)

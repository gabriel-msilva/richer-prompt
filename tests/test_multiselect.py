from unittest.mock import patch

import pytest
import readchar

from richer_prompt.models import MultiSelectionModel
from richer_prompt.options import Option
from richer_prompt.prompt.multiselect import MultiSelect
from tests.utils import assert_snapshot, simulate


@pytest.fixture
def multiselect(console) -> MultiSelect:
    return MultiSelect("Select multiple options:", ["a", "b", "c"], console=console)


def test_that_options_are_selected(multiselect: MultiSelect):
    result = simulate(
        multiselect,
        [
            readchar.key.ENTER,
            readchar.key.DOWN,
            readchar.key.DOWN,
            readchar.key.ENTER,
            readchar.key.DOWN,
            readchar.key.ENTER,
        ],
    )

    assert result == ["a", "c"]


def test_that_options_can_be_unselected(multiselect: MultiSelect):
    result = simulate(
        multiselect,
        [
            readchar.key.ENTER,
            readchar.key.DOWN,
            readchar.key.ENTER,
            readchar.key.ENTER,
            readchar.key.DOWN,
            readchar.key.DOWN,
            readchar.key.ENTER,
        ],
    )

    assert result == ["a"]


def test_that_space_toggles(multiselect: MultiSelect):
    result = simulate(
        multiselect,
        [readchar.key.SPACE, readchar.key.UP, readchar.key.ENTER],
    )

    assert result == ["a"]


def test_that_space_toggle_on_submit_is_noop(multiselect: MultiSelect):
    result = simulate(
        multiselect,
        [readchar.key.UP, readchar.key.SPACE, readchar.key.ENTER],
    )

    assert result == []


def test_that_number_key_move_and_check(multiselect: MultiSelect):
    result = simulate(
        multiselect,
        ["0", "2", readchar.key.DOWN, readchar.key.DOWN, readchar.key.ENTER],
    )

    assert result == ["b"]


def test_that_number_key_out_of_range_is_ignored(multiselect: MultiSelect):
    result = simulate(multiselect, ["0", "4", readchar.key.UP, readchar.key.ENTER])

    assert result == []


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

    assert simulate(multiselect, keys) == ["a"]


def test_that_cursor_starts_at_index(multiselect: MultiSelect):
    result = simulate(
        multiselect,
        [readchar.key.ENTER, readchar.key.DOWN, readchar.key.ENTER],
        index=2,
    )

    assert result == ["c"]


def test_that_cursor_can_start_at_submit(multiselect: MultiSelect):
    result = simulate(multiselect, [readchar.key.ENTER], index=3)

    assert result == []


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
    result = simulate(
        multiselect, [readchar.key.UP, readchar.key.ENTER], default=default
    )

    assert result == expected


def test_that_default_indices_out_of_range_raises(multiselect):
    with pytest.raises(
        ValueError, match="Default indices \\[-1, 3\\] are out of range"
    ):
        multiselect(default={-1, 0, 1, 3})


def test_ask():
    with patch(
        "richer_prompt.models.readchar.readkey",
        side_effect=[readchar.key.ENTER, readchar.key.DOWN, readchar.key.ENTER],
    ):
        assert MultiSelect.ask("Pick", ["a", "b", "c"], index=2) == ["c"]


def test_that_answer_is_not_affected_by_subsequent_calls(multiselect: MultiSelect):
    first = simulate(
        multiselect, [readchar.key.ENTER, readchar.key.UP, readchar.key.ENTER]
    )

    assert first == ["a"]

    second = simulate(
        multiselect,
        [
            readchar.key.DOWN,
            readchar.key.ENTER,
            readchar.key.DOWN,
            readchar.key.DOWN,
            readchar.key.ENTER,
        ],
    )

    assert second == ["b"]


def test_that_answer_is_rendered(multiselect: MultiSelect):
    with multiselect.console.capture() as capture:
        simulate(
            multiselect,
            [
                readchar.key.ENTER,
                readchar.key.DOWN,
                readchar.key.DOWN,
                readchar.key.ENTER,
                readchar.key.DOWN,
                readchar.key.ENTER,
            ],
        )

    assert capture.get() == "Select multiple options: a, c\n"


def test_that_str_options_are_rendered(multiselect: MultiSelect):
    model = MultiSelectionModel(multiselect.options)

    expected = """
    Select multiple options:

    ❯ 1. [ ] a
      2. [ ] b
      3. [ ] c
         Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(multiselect, model, expected)


def test_that_labels_and_descriptions_are_rendered():
    prompt = MultiSelect(
        "Select multiple options:",
        [
            Option(value="a", label="Option A"),
            Option(value="b", description="The second option"),
            Option(value="c", label="Option C", description="The third option"),
        ],
    )

    model = MultiSelectionModel(prompt.options)

    expected = """
    Select multiple options:

    ❯ 1. [ ] Option A
      2. [ ] b  The second option
      3. [ ] Option C  The third option
         Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(prompt, model, expected)


def test_that_options_are_rendered_without_numbers():
    prompt = MultiSelect("Select multiple options:", ["a", "b", "c"], numbered=False)
    model = MultiSelectionModel(prompt.options)

    expected = """
    Select multiple options:

    ❯ [ ] a
      [ ] b
      [ ] c
      Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(prompt, model, expected)


def test_that_cursor_pointer_moves(multiselect: MultiSelect):
    model = MultiSelectionModel(multiselect.options, cursor=1)

    expected = """
    Select multiple options:

      1. [ ] a
    ❯ 2. [ ] b
      3. [ ] c
         Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(multiselect, model, expected)


def test_that_checkbox_indicators_are_rendered(multiselect: MultiSelect):
    model = MultiSelectionModel(multiselect.options, selected={0, 2})

    expected = """
    Select multiple options:

    ❯ 1. [✓] a
      2. [ ] b
      3. [✓] c
         Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(multiselect, model, expected)


def test_custom_pointer():
    multiselect = MultiSelect(
        "Select multiple options:", ["a", "b", "c"], cursor_pointer=">>"
    )
    model = MultiSelectionModel(multiselect.options)

    expected = """
    Select multiple options:

    >> 1. [ ] a
       2. [ ] b
       3. [ ] c
          Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(multiselect, model, expected)


def test_that_hint_is_hidden():
    prompt = MultiSelect("Select multiple options:", ["a", "b", "c"], show_hint=False)
    model = MultiSelectionModel(prompt.options)

    expected = """
    Select multiple options:

    ❯ 1. [ ] a
      2. [ ] b
      3. [ ] c
         Submit
    """

    assert_snapshot(prompt, model, expected)


def test_that_10_or_more_options_are_aligned():
    prompt = MultiSelect(
        "Select multiple options:", [f"Option {i}" for i in range(1, 11)]
    )
    model = MultiSelectionModel(prompt.options)

    expected = """
    Select multiple options:

    ❯  1. [ ] Option 1
       2. [ ] Option 2
       3. [ ] Option 3
       4. [ ] Option 4
       5. [ ] Option 5
       6. [ ] Option 6
       7. [ ] Option 7
       8. [ ] Option 8
       9. [ ] Option 9
      10. [ ] Option 10
          Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(prompt, model, expected)


def test_style():
    prompt = MultiSelect(
        "Select multiple options:",
        [
            Option("a", description="The first option"),
            Option("b", description="The second option"),
            Option("c", description="The third option"),
        ],
    )

    model = MultiSelectionModel(prompt.options, selected={0})
    expected = """
    [richer_prompt.title]Select multiple options:[/]

    [richer_prompt.cursor]❯[/] [richer_prompt.description]1. [/][richer_prompt.checkbox.checked][✓][/] [richer_prompt.cursor]a[/]  [richer_prompt.description]The first option[/]
      [richer_prompt.description]2. [/][ ] b  [richer_prompt.description]The second option[/]
      [richer_prompt.description]3. [/][ ] c  [richer_prompt.description]The third option[/]
         Submit

    [richer_prompt.hint]↑↓ to navigate · Enter to select · Submit to finish[/]
    """

    assert_snapshot(prompt, model, expected, raw=True)

    model = MultiSelectionModel(prompt.options, cursor=3)
    expected = """
    [richer_prompt.title]Select multiple options:[/]

      [richer_prompt.description]1. [/][ ] a  [richer_prompt.description]The first option[/]
      [richer_prompt.description]2. [/][ ] b  [richer_prompt.description]The second option[/]
      [richer_prompt.description]3. [/][ ] c  [richer_prompt.description]The third option[/]
    [richer_prompt.cursor]❯[/]    [richer_prompt.cursor]Submit[/]

    [richer_prompt.hint]↑↓ to navigate · Enter to select · Submit to finish[/]
    """

    assert_snapshot(prompt, model, expected, raw=True)

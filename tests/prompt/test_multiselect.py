import pytest
from rich.console import Console

from richer_prompt import keys
from richer_prompt.choices import Choice
from richer_prompt.prompt.multiselect import MultiSelect
from richer_prompt.testing import simulate_keys
from tests.utils import assert_snapshot


@pytest.fixture
def multiselect(console) -> MultiSelect:
    return MultiSelect("Select multiple choices:", ["a", "b", "c"], console=console)


def test_that_choices_are_selected(multiselect: MultiSelect):
    with simulate_keys(
        [
            keys.ENTER,
            keys.DOWN,
            keys.DOWN,
            keys.ENTER,
            keys.DOWN,
            keys.ENTER,
        ]
    ):
        assert multiselect() == ["a", "c"]


def test_that_choices_can_be_unselected(multiselect: MultiSelect):
    with simulate_keys(
        [
            keys.ENTER,
            keys.DOWN,
            keys.ENTER,
            keys.ENTER,
            keys.DOWN,
            keys.DOWN,
            keys.ENTER,
        ]
    ):
        assert multiselect() == ["a"]


def test_that_space_toggles(multiselect: MultiSelect):
    with simulate_keys([keys.SPACE, keys.UP, keys.ENTER]):
        assert multiselect() == ["a"]


def test_that_space_toggle_on_submit_is_noop(multiselect: MultiSelect):
    with simulate_keys([keys.UP, keys.SPACE, keys.ENTER]):
        assert multiselect() == []


def test_that_number_key_move_and_check(multiselect: MultiSelect):
    with simulate_keys(["2", keys.DOWN, keys.DOWN, keys.ENTER]):
        assert multiselect() == ["b"]


def test_that_number_key_out_of_range_is_ignored(multiselect: MultiSelect):
    with simulate_keys(["0", "4", keys.UP, keys.ENTER]):
        assert multiselect() == []


def test_that_numbering_is_disabled_for_more_than_9_choices(console):
    multiselect = MultiSelect(
        "Select multiple choices:",
        [f"Choice {i}" for i in range(1, 13)],
        console=console,
    )

    with simulate_keys(["1", keys.UP, keys.ENTER]):
        assert multiselect() == []


def test_that_digit_keys_work_when_numbers_enabled(console):
    multiselect = MultiSelect(
        "Select multiple choices:",
        [f"Choice {i}" for i in range(1, 13)],
        numbered=True,
        console=console,
    )

    with simulate_keys(["2", keys.UP, keys.UP, keys.ENTER]):
        assert multiselect() == ["Choice 2"]


def test_that_digit_keys_are_inert_when_numbering_disabled(console):
    multiselect = MultiSelect(
        "Select multiple choices:", ["a", "b", "c"], numbered=False, console=console
    )

    with simulate_keys(["2", keys.UP, keys.ENTER]):
        assert multiselect() == []


def test_rollover(multiselect: MultiSelect):
    with simulate_keys(
        [
            keys.UP,
            keys.DOWN,
            keys.ENTER,
            keys.DOWN,
            keys.DOWN,
            keys.DOWN,
            keys.ENTER,
        ]
    ):
        assert multiselect() == ["a"]


def test_that_cursor_starts_at_index(multiselect: MultiSelect):
    with simulate_keys([keys.ENTER, keys.DOWN, keys.ENTER]):
        assert multiselect(index=2) == ["c"]


def test_that_cursor_can_start_at_submit(multiselect: MultiSelect):
    with simulate_keys([keys.ENTER]):
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
    with simulate_keys([keys.UP, keys.ENTER]):
        assert multiselect(default=default) == expected


def test_that_default_indices_out_of_range_raises(multiselect):
    with pytest.raises(
        ValueError, match="Default indices \\[-1, 3\\] are out of range"
    ):
        multiselect(default={-1, 0, 1, 3})


@pytest.mark.parametrize(("height", "expected"), [(12, 6), (5, 3)])
def test_that_viewport_size_defaults_to_terminal_height(height, expected):
    console = Console(width=60, height=height, color_system=None, force_terminal=False)
    multiselect = MultiSelect(
        "Select multiple choices:", [f"Choice {i}" for i in range(20)], console=console
    )

    assert multiselect._build_widget().viewport_size == expected


def test_ask():
    with simulate_keys([keys.ENTER, keys.DOWN, keys.ENTER]):
        assert MultiSelect.ask("Pick", ["a", "b", "c"], index=2) == ["c"]


def test_that_answer_is_not_affected_by_subsequent_calls(multiselect: MultiSelect):
    with simulate_keys([keys.ENTER, keys.UP, keys.ENTER]):
        assert multiselect() == ["a"]

    with simulate_keys(
        [
            keys.DOWN,
            keys.ENTER,
            keys.DOWN,
            keys.DOWN,
            keys.ENTER,
        ]
    ):
        assert multiselect() == ["b"]


def test_that_answer_is_rendered(multiselect: MultiSelect):
    with (
        multiselect.console.capture() as capture,
        simulate_keys(
            [
                keys.ENTER,
                keys.DOWN,
                keys.DOWN,
                keys.ENTER,
                keys.DOWN,
                keys.ENTER,
            ]
        ),
    ):
        multiselect()

    assert capture.get() == "Select multiple choices: a, c\n"


def test_that_str_choices_are_rendered(multiselect: MultiSelect):
    expected = """
    Select multiple choices:

    ❯ 1. [ ] a
      2. [ ] b
      3. [ ] c
         Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(multiselect, expected)


def test_that_labels_and_descriptions_are_rendered():
    prompt = MultiSelect(
        "Select multiple choices:",
        [
            Choice(value="a", label="Choice A"),
            Choice(value="b", description="The second choice"),
            Choice(value="c", label="Choice C", description="The third choice"),
        ],
    )

    expected = """
    Select multiple choices:

    ❯ 1. [ ] Choice A
      2. [ ] b  The second choice
      3. [ ] Choice C  The third choice
         Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(prompt, expected)


def test_that_choices_are_rendered_without_numbers():
    prompt = MultiSelect("Select multiple choices:", ["a", "b", "c"], numbered=False)
    expected = """
    Select multiple choices:

    ❯ [ ] a
      [ ] b
      [ ] c
      Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(prompt, expected)


def test_that_cursor_pointer_moves(multiselect: MultiSelect):
    expected = """
    Select multiple choices:

      1. [ ] a
    ❯ 2. [ ] b
      3. [ ] c
         Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(multiselect, expected, index=1)


def test_that_checkbox_indicators_are_rendered(multiselect: MultiSelect):
    expected = """
    Select multiple choices:

    ❯ 1. [✓] a
      2. [ ] b
      3. [✓] c
         Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(multiselect, expected, default={0, 2})


def test_custom_pointer():
    multiselect = MultiSelect(
        "Select multiple choices:", ["a", "b", "c"], cursor_pointer=">>"
    )
    expected = """
    Select multiple choices:

    >> 1. [ ] a
       2. [ ] b
       3. [ ] c
          Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(multiselect, expected)


def test_that_hint_is_hidden():
    prompt = MultiSelect("Select multiple choices:", ["a", "b", "c"], show_hint=False)
    expected = """
    Select multiple choices:

    ❯ 1. [ ] a
      2. [ ] b
      3. [ ] c
         Submit
    """

    assert_snapshot(prompt, expected)


def test_that_10_or_more_choices_are_aligned(console):
    prompt = MultiSelect(
        "Select multiple choices:",
        [f"Choice {i}" for i in range(1, 11)],
        numbered=True,
        console=console,
    )
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

    assert_snapshot(prompt, expected)


def test_that_numbers_auto_hide_for_more_than_9_choices(console):
    prompt = MultiSelect(
        "Select multiple choices:",
        [f"Choice {i}" for i in range(1, 11)],
        console=console,
    )
    expected = """
    Select multiple choices:

    ❯ [ ] Choice 1
      [ ] Choice 2
      [ ] Choice 3
      [ ] Choice 4
      [ ] Choice 5
      [ ] Choice 6
      [ ] Choice 7
      [ ] Choice 8
      [ ] Choice 9
      [ ] Choice 10
      Submit

    ↑↓ to navigate · Enter to select · Submit to finish
    """

    assert_snapshot(prompt, expected)


@pytest.mark.parametrize(
    ("index", "expected"),
    [
        (
            0,
            """
            Select multiple choices:

            ❯ [ ] Choice 1
              [ ] Choice 2
              [ ] Choice 3
            ↓ [ ] Choice 4
              Submit

            ↑↓ to navigate · Enter to select · Submit to finish
            """,
        ),
        (
            2,
            """
            Select multiple choices:

            ↑ [ ] Choice 2
            ❯ [ ] Choice 3
              [ ] Choice 4
            ↓ [ ] Choice 5
              Submit

            ↑↓ to navigate · Enter to select · Submit to finish
            """,
        ),
        (
            5,
            """
            Select multiple choices:

            ↑ [ ] Choice 3
              [ ] Choice 4
              [ ] Choice 5
            ❯ [ ] Choice 6
              Submit

            ↑↓ to navigate · Enter to select · Submit to finish
            """,
        ),
        (
            6,
            """
            Select multiple choices:

            ↑ [ ] Choice 3
              [ ] Choice 4
              [ ] Choice 5
              [ ] Choice 6
            ❯ Submit

            ↑↓ to navigate · Enter to select · Submit to finish
            """,
        ),
    ],
    ids=["top", "middle", "bottom", "submit"],
)
def test_that_viewport_is_scrolled(index, expected):
    multiselect = MultiSelect(
        "Select multiple choices:",
        [f"Choice {i + 1}" for i in range(6)],
        viewport_size=4,
    )

    assert_snapshot(multiselect, expected, index=index)


def test_style():
    prompt = MultiSelect(
        "Select multiple choices:",
        [
            Choice("a", description="The first choice"),
            Choice("b", description="The second choice"),
            Choice("c", description="The third choice"),
        ],
    )

    expected = """
    [richer_prompt.title]Select multiple choices:[/]

    [richer_prompt.cursor]❯[/] [richer_prompt.description]1. [/][richer_prompt.checkbox.checked][✓][/] [richer_prompt.cursor]a[/]  [richer_prompt.description]The first choice[/]
      [richer_prompt.description]2. [/][ ] b  [richer_prompt.description]The second choice[/]
      [richer_prompt.description]3. [/][ ] c  [richer_prompt.description]The third choice[/]
         Submit

    [richer_prompt.hint]↑↓ to navigate · Enter to select · Submit to finish[/]
    """

    assert_snapshot(prompt, expected, default={0}, raw=True)

    expected = """
    [richer_prompt.title]Select multiple choices:[/]

      [richer_prompt.description]1. [/][ ] a  [richer_prompt.description]The first choice[/]
      [richer_prompt.description]2. [/][ ] b  [richer_prompt.description]The second choice[/]
      [richer_prompt.description]3. [/][ ] c  [richer_prompt.description]The third choice[/]
    [richer_prompt.cursor]❯[/]    [richer_prompt.cursor]Submit[/]

    [richer_prompt.hint]↑↓ to navigate · Enter to select · Submit to finish[/]
    """

    assert_snapshot(prompt, expected, index=3, raw=True)

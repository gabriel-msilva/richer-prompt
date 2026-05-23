from unittest.mock import patch

import pytest
import readchar

from richer_prompt.models import SingleSelectionModel
from richer_prompt.options import Option
from richer_prompt.prompt.select import Select
from tests.utils import assert_snapshot, simulate


@pytest.fixture
def select(console) -> Select:
    return Select("Select an option", ["a", "b", "c"], console=console)


def test_that_option_is_selected(select: Select):
    result = simulate(
        select,
        [
            readchar.key.DOWN,
            readchar.key.DOWN,
            readchar.key.UP,
            readchar.key.ENTER,
        ],
    )

    assert result == "b"


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (0, "a"),  # Zero is ignored and treated as Enter on cursor 0
        (1, "a"),
        (2, "b"),
        (3, "c"),
        (4, "a"),  # Out of range rolls over to first option
    ],
)
def test_that_number_key_selects(select: Select, number: int, expected: str):
    assert simulate(select, [str(number), readchar.key.ENTER]) == expected


@pytest.mark.parametrize(
    ("keys", "expected"),
    [
        ([readchar.key.UP, readchar.key.ENTER], "c"),
        (
            [
                readchar.key.DOWN,
                readchar.key.DOWN,
                readchar.key.DOWN,
                readchar.key.ENTER,
            ],
            "a",
        ),
    ],
    ids=["up", "down"],
)
def test_rollover(select: Select, keys, expected):
    assert simulate(select, keys) == expected


def test_that_cursor_starts_at_index(select: Select):
    assert simulate(select, [readchar.key.ENTER], index=1) == "b"


@pytest.mark.parametrize("index", [-1, 3])
def test_that_index_out_of_range_raises(select: Select, index):
    with pytest.raises(ValueError, match=f"Index '{index}' is out of range"):
        select(index=index)


def test_ask():
    with patch(
        "richer_prompt.models.readchar.readkey",
        side_effect=[readchar.key.UP, readchar.key.ENTER],
    ):
        assert Select.ask("Select an option", ["a", "b", "c"], index=1) == "a"


def test_that_answer_is_rendered(select: Select):
    with select.console.capture() as capture:
        simulate(select, [readchar.key.DOWN, readchar.key.ENTER])

    assert capture.get() == "Select an option: b\n"


def test_that_str_options_are_rendered(select: Select):
    model = SingleSelectionModel(select.options)

    expected = """
    Select an option:

    ❯ 1. a
      2. b
      3. c

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(select, model, expected)


def test_that_labels_and_descriptions_are_rendered():
    prompt = Select(
        "Select an option",
        [
            Option(value="a", label="Option A"),
            Option(value="b", description="The second option"),
            Option(value="c", label="Option C", description="The third option"),
        ],
    )

    model = SingleSelectionModel(prompt.options)

    expected = """
    Select an option:

    ❯ 1. Option A
      2. b  The second option
      3. Option C  The third option

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(prompt, model, expected)


def test_that_options_are_rendered_without_numbers():
    select = Select("Select an option", ["a", "b", "c"], numbered=False)
    model = SingleSelectionModel(select.options)

    expected = """
    Select an option:

    ❯ a
      b
      c

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(select, model, expected)


def test_that_cursor_pointer_moves(select: Select):
    model = SingleSelectionModel(select.options, cursor=1)

    expected = """
    Select an option:

      1. a
    ❯ 2. b
      3. c

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(select, model, expected)


def test_custom_pointer():
    prompt = Select("Select an option", ["a", "b", "c"], cursor_pointer=">>")
    model = SingleSelectionModel(prompt.options)

    expected = """
    Select an option:

    >> 1. a
       2. b
       3. c

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(prompt, model, expected)


def test_that_hint_is_hidden():
    prompt = Select("Select an option", ["a", "b", "c"], show_hint=False)
    model = SingleSelectionModel(prompt.options)

    expected = """
    Select an option:

    ❯ 1. a
      2. b
      3. c
    """

    assert_snapshot(prompt, model, expected)


def test_that_10_or_more_options_are_aligned():
    prompt = Select("Select an option", [f"Option {i}" for i in range(1, 11)])
    model = SingleSelectionModel(prompt.options)

    expected = """
    Select an option:

    ❯  1. Option 1
       2. Option 2
       3. Option 3
       4. Option 4
       5. Option 5
       6. Option 6
       7. Option 7
       8. Option 8
       9. Option 9
      10. Option 10

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(prompt, model, expected)


def test_style():
    prompt = Select(
        "Select an option",
        [
            Option("a", description="The first option"),
            Option("b", description="The second option"),
            Option("c", description="The third option"),
        ],
    )

    model = SingleSelectionModel(prompt.options)

    expected = """
    [richer_prompt.title]Select an option:[/]

    [richer_prompt.cursor]❯[/] [richer_prompt.description]1. [/][richer_prompt.cursor]a[/]  [richer_prompt.description]The first option[/]
      [richer_prompt.description]2. [/][richer_prompt.option]b[/]  [richer_prompt.description]The second option[/]
      [richer_prompt.description]3. [/][richer_prompt.option]c[/]  [richer_prompt.description]The third option[/]

    [richer_prompt.hint]↑↓ to navigate · Enter to select[/]
    """

    assert_snapshot(prompt, model, expected, raw=True)

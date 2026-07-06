import pytest
import readchar

from richer_prompt.choices import Choice
from richer_prompt.prompt.select import Select
from tests.utils import assert_snapshot, simulate, simulate_keys


@pytest.fixture
def select(console) -> Select:
    return Select("Select a choice:", ["a", "b", "c"], console=console)


def test_that_choice_is_selected(select: Select):
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
        (4, "a"),  # Out of range rolls over to first choice
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
    with simulate_keys([readchar.key.UP, readchar.key.ENTER]):
        assert Select.ask("Select a choice:", ["a", "b", "c"], index=1) == "a"


def test_that_answer_is_rendered(select: Select):
    with select.console.capture() as capture:
        simulate(select, [readchar.key.DOWN, readchar.key.ENTER])

    assert capture.get() == "Select a choice: b\n"


def test_that_str_choices_are_rendered(select: Select):
    widget = select._build_widget()

    expected = """
    Select a choice:

    ❯ 1. a
      2. b
      3. c

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(widget, expected)


def test_that_labels_and_descriptions_are_rendered():
    prompt = Select(
        "Select a choice:",
        [
            Choice(value="a", label="Choice A"),
            Choice(value="b", description="The second choice"),
            Choice(value="c", label="Choice C", description="The third choice"),
        ],
    )

    widget = prompt._build_widget()

    expected = """
    Select a choice:

    ❯ 1. Choice A
      2. b  The second choice
      3. Choice C  The third choice

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(widget, expected)


def test_that_choices_are_rendered_without_numbers():
    select = Select("Select a choice:", ["a", "b", "c"], numbered=False)
    widget = select._build_widget()

    expected = """
    Select a choice:

    ❯ a
      b
      c

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(widget, expected)


def test_that_cursor_pointer_moves(select: Select):
    widget = select._build_widget(index=1)

    expected = """
    Select a choice:

      1. a
    ❯ 2. b
      3. c

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(widget, expected)


def test_custom_pointer():
    prompt = Select("Select a choice:", ["a", "b", "c"], cursor_pointer=">>")
    widget = prompt._build_widget()

    expected = """
    Select a choice:

    >> 1. a
       2. b
       3. c

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(widget, expected)


def test_that_hint_is_hidden():
    prompt = Select("Select a choice:", ["a", "b", "c"], show_hint=False)
    widget = prompt._build_widget()

    expected = """
    Select a choice:

    ❯ 1. a
      2. b
      3. c
    """

    assert_snapshot(widget, expected)


def test_that_10_or_more_choices_are_aligned():
    prompt = Select("Select a choice:", [f"Choice {i}" for i in range(1, 11)])
    widget = prompt._build_widget()

    expected = """
    Select a choice:

    ❯  1. Choice 1
       2. Choice 2
       3. Choice 3
       4. Choice 4
       5. Choice 5
       6. Choice 6
       7. Choice 7
       8. Choice 8
       9. Choice 9
      10. Choice 10

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(widget, expected)


def test_style():
    prompt = Select(
        "Select a choice:",
        [
            Choice("a", description="The first choice"),
            Choice("b", description="The second choice"),
            Choice("c", description="The third choice"),
        ],
    )

    widget = prompt._build_widget()

    expected = """
    [richer_prompt.title]Select a choice:[/]

    [richer_prompt.cursor]❯[/] [richer_prompt.description]1. [/][richer_prompt.cursor]a[/]  [richer_prompt.description]The first choice[/]
      [richer_prompt.description]2. [/][richer_prompt.choice]b[/]  [richer_prompt.description]The second choice[/]
      [richer_prompt.description]3. [/][richer_prompt.choice]c[/]  [richer_prompt.description]The third choice[/]

    [richer_prompt.hint]↑↓ to navigate · Enter to select[/]
    """

    assert_snapshot(widget, expected, raw=True)

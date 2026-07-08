import pytest

from richer_prompt import keys
from richer_prompt.choices import Choice
from richer_prompt.prompt.select import Select
from richer_prompt.testing import simulate_keys
from tests.utils import assert_snapshot


@pytest.fixture
def select(console) -> Select:
    return Select("Select a choice:", ["a", "b", "c"], console=console)


def test_that_choice_is_selected(select: Select):
    with simulate_keys(
        [
            keys.DOWN,
            keys.DOWN,
            keys.UP,
            keys.ENTER,
        ]
    ):
        assert select() == "b"


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
    with simulate_keys([str(number), keys.ENTER]):
        assert select() == expected


def test_that_numbering_is_disabled_for_more_than_9_choices(console):
    select = Select(
        "Select a choice:", [f"Choice {i}" for i in range(1, 13)], console=console
    )

    with simulate_keys(["5", keys.ENTER]):
        assert select() == "Choice 1"


def test_that_digit_keys_work_when_numbers_enabled(console):
    select = Select(
        "Select a choice:",
        [f"Choice {i}" for i in range(1, 13)],
        numbered=True,
        console=console,
    )

    with simulate_keys(["5", keys.ENTER]):
        assert select() == "Choice 5"


def test_that_digit_keys_are_inert_when_numbering_disabled(console):
    select = Select(
        "Select a choice:", ["a", "b", "c"], numbered=False, console=console
    )

    with simulate_keys(["2", keys.ENTER]):
        assert select() == "a"


@pytest.mark.parametrize(
    ("keys", "expected"),
    [
        ([keys.UP, keys.ENTER], "c"),
        (
            [
                keys.DOWN,
                keys.DOWN,
                keys.DOWN,
                keys.ENTER,
            ],
            "a",
        ),
    ],
    ids=["up", "down"],
)
def test_rollover(select: Select, keys, expected):
    with simulate_keys(keys):
        assert select() == expected


def test_that_cursor_starts_at_index(select: Select):
    with simulate_keys([keys.ENTER]):
        assert select(index=1) == "b"


@pytest.mark.parametrize("index", [-1, 3])
def test_that_index_out_of_range_raises(select: Select, index):
    with pytest.raises(ValueError, match=f"Index '{index}' is out of range"):
        select(index=index)


def test_ask():
    with simulate_keys([keys.UP, keys.ENTER]):
        assert Select.ask("Select a choice:", ["a", "b", "c"], index=1) == "a"


def test_that_answer_is_rendered(select: Select):
    with (
        select.console.capture() as capture,
        simulate_keys([keys.DOWN, keys.ENTER]),
    ):
        select()

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
    prompt = Select(
        "Select a choice:", [f"Choice {i}" for i in range(1, 11)], numbered=True
    )
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


def test_that_numbers_auto_hide_for_more_than_9_choices():
    prompt = Select("Select a choice:", [f"Choice {i}" for i in range(1, 11)])
    widget = prompt._build_widget()

    expected = """
    Select a choice:

    ❯ Choice 1
      Choice 2
      Choice 3
      Choice 4
      Choice 5
      Choice 6
      Choice 7
      Choice 8
      Choice 9
      Choice 10

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

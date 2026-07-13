import pytest
from rich.console import Console

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
        keys.DOWN,
        keys.DOWN,
        keys.UP,
        keys.ENTER,
    ):
        assert select() == "b"


def test_that_vim_keys_navigate(select: Select):
    with simulate_keys("j", "j", "k", keys.ENTER):
        assert select() == "b"


def test_that_horizontal_vim_keys_are_inert(select: Select):
    with simulate_keys("h", "l", keys.ENTER):
        assert select() == "a"


def test_that_end_key_jumps_to_last_choice(select: Select):
    with simulate_keys(keys.END, keys.ENTER):
        assert select() == "c"


def test_that_home_key_jumps_to_first_choice(select: Select):
    with simulate_keys(keys.DOWN, keys.DOWN, keys.HOME, keys.ENTER):
        assert select() == "a"


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
    with simulate_keys(str(number), keys.ENTER):
        assert select() == expected


def test_that_numbering_is_disabled_for_more_than_9_choices(console):
    select = Select(
        "Select a choice:", [f"Choice {i}" for i in range(1, 13)], console=console
    )

    with simulate_keys("5", keys.ENTER):
        assert select() == "Choice 1"


def test_that_digit_keys_work_when_numbers_enabled(console):
    select = Select(
        "Select a choice:",
        [f"Choice {i}" for i in range(1, 13)],
        numbered=True,
        console=console,
    )

    with simulate_keys("5", keys.ENTER):
        assert select() == "Choice 5"


def test_that_digit_keys_are_inert_when_numbering_disabled(console):
    select = Select(
        "Select a choice:", ["a", "b", "c"], numbered=False, console=console
    )

    with simulate_keys("2", keys.ENTER):
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
    with simulate_keys(*keys):
        assert select() == expected


def test_that_cursor_starts_at_index(select: Select):
    with simulate_keys(keys.ENTER):
        assert select(index=1) == "b"


@pytest.mark.parametrize("index", [-1, 3])
def test_that_index_out_of_range_raises(select: Select, index):
    with pytest.raises(ValueError, match=f"Index '{index}' is out of range"):
        select(index=index)


@pytest.mark.parametrize(("height", "expected"), [(12, 7), (5, 3)])
def test_that_viewport_size_defaults_to_terminal_height(height, expected):
    console = Console(width=60, height=height, color_system=None, force_terminal=False)
    select = Select(
        "Select a choice:", [f"Choice {i}" for i in range(20)], console=console
    )

    assert select._build_widget().viewport_size == expected


def test_ask():
    with simulate_keys(keys.UP, keys.ENTER):
        assert Select.ask("Select a choice:", ["a", "b", "c"], index=1) == "a"


def test_that_answer_is_rendered(select: Select):
    with (
        select.console.capture() as capture,
        simulate_keys(keys.DOWN, keys.ENTER),
    ):
        select()

    assert capture.get() == "Select a choice: b\n"


def test_that_str_choices_are_rendered(select: Select):
    expected = """
    Select a choice:

    ❯ 1. a
      2. b
      3. c

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(select, expected)


def test_that_labels_and_descriptions_are_rendered():
    prompt = Select(
        "Select a choice:",
        [
            Choice(value="a", label="Choice A"),
            Choice(value="b", description="The second choice"),
            Choice(value="c", label="Choice C", description="The third choice"),
        ],
    )

    expected = """
    Select a choice:

    ❯ 1. Choice A
      2. b  The second choice
      3. Choice C  The third choice

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(prompt, expected)


def test_that_choices_are_rendered_without_numbers():
    select = Select("Select a choice:", ["a", "b", "c"], numbered=False)
    expected = """
    Select a choice:

    ❯ a
      b
      c

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(select, expected)


def test_that_cursor_pointer_moves(select: Select):
    expected = """
    Select a choice:

      1. a
    ❯ 2. b
      3. c

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(select, expected, index=1)


def test_custom_pointer():
    prompt = Select("Select a choice:", ["a", "b", "c"], cursor_pointer=">>")
    expected = """
    Select a choice:

    >> 1. a
       2. b
       3. c

    ↑↓ to navigate · Enter to select
    """

    assert_snapshot(prompt, expected)


def test_that_hint_is_hidden():
    prompt = Select("Select a choice:", ["a", "b", "c"], show_hint=False)
    expected = """
    Select a choice:

    ❯ 1. a
      2. b
      3. c
    """

    assert_snapshot(prompt, expected)


def test_that_10_or_more_choices_are_aligned(console):
    prompt = Select(
        "Select a choice:",
        [f"Choice {i}" for i in range(1, 11)],
        numbered=True,
        console=console,
    )
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

    assert_snapshot(prompt, expected)


def test_that_numbers_auto_hide_for_more_than_9_choices(console):
    prompt = Select(
        "Select a choice:", [f"Choice {i}" for i in range(1, 11)], console=console
    )
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

    assert_snapshot(prompt, expected)


@pytest.mark.parametrize(
    ("index", "expected"),
    [
        (
            0,
            """
            Select a choice:

            ❯ Choice 1
              Choice 2
              Choice 3
            ↓ Choice 4

            ↑↓ to navigate · Enter to select
            """,
        ),
        (
            2,
            """
            Select a choice:

            ↑ Choice 2
            ❯ Choice 3
              Choice 4
            ↓ Choice 5

            ↑↓ to navigate · Enter to select
            """,
        ),
        (
            5,
            """
            Select a choice:

            ↑ Choice 3
              Choice 4
              Choice 5
            ❯ Choice 6

            ↑↓ to navigate · Enter to select
            """,
        ),
    ],
    ids=["top", "middle", "bottom"],
)
def test_that_viewport_is_scrolled(index, expected):
    select = Select(
        "Select a choice:", [f"Choice {i + 1}" for i in range(6)], viewport_size=4
    )

    assert_snapshot(select, expected, index=index)


def test_style():
    prompt = Select(
        "Select a choice:",
        [
            Choice("a", description="The first choice"),
            Choice("b", description="The second choice"),
            Choice("c", description="The third choice"),
        ],
    )

    expected = """
    [richer_prompt.title]Select a choice:[/]

    [richer_prompt.cursor]❯[/] [richer_prompt.description]1. [/][richer_prompt.cursor]a[/]  [richer_prompt.description]The first choice[/]
      [richer_prompt.description]2. [/][richer_prompt.choice]b[/]  [richer_prompt.description]The second choice[/]
      [richer_prompt.description]3. [/][richer_prompt.choice]c[/]  [richer_prompt.description]The third choice[/]

    [richer_prompt.hint]↑↓ to navigate · Enter to select[/]
    """

    assert_snapshot(prompt, expected, raw=True)

import pytest

from richer_prompt import keys
from richer_prompt.choices import Choice
from richer_prompt.prompt.tabs import Tabs
from richer_prompt.testing import simulate_keys
from tests.utils import assert_snapshot


@pytest.fixture
def tabs(console) -> Tabs:
    return Tabs("Select a choice:", ["a", "b", "c"], console=console)


def test_that_choice_is_selected(tabs: Tabs):
    with simulate_keys(
        [
            keys.RIGHT,
            keys.TAB,
            keys.LEFT,
            keys.ENTER,
        ]
    ):
        assert tabs() == "b"


def test_that_shift_tab_move_to_previous(tabs: Tabs):
    with simulate_keys(
        [
            keys.TAB,
            keys.TAB,
            keys.SHIFT_TAB,
            keys.ENTER,
        ]
    ):
        assert tabs() == "b"


@pytest.mark.parametrize(
    ("keys", "expected"),
    [
        ([keys.LEFT, keys.ENTER], "a"),
        (
            [
                keys.RIGHT,
                keys.RIGHT,
                keys.RIGHT,
                keys.ENTER,
            ],
            "c",
        ),
    ],
    ids=["left", "right"],
)
def test_that_cursor_doesnt_rollover(tabs: Tabs, keys, expected):
    with simulate_keys(keys):
        assert tabs() == expected


def test_that_cursor_starts_at_index(tabs: Tabs):
    with simulate_keys([keys.ENTER]):
        assert tabs(index=1) == "b"


@pytest.mark.parametrize("index", [-1, 3])
def test_that_index_out_of_range_raises(tabs: Tabs, index):
    with pytest.raises(ValueError, match=f"Index '{index}' is out of range"):
        tabs(index=index)


def test_ask():
    with simulate_keys([keys.RIGHT, keys.ENTER]):
        assert Tabs.ask("Select a choice:", ["a", "b", "c"], index=1) == "c"


def test_that_answer_is_rendered(tabs: Tabs):
    with (
        tabs.console.capture() as capture,
        simulate_keys([keys.RIGHT, keys.ENTER]),
    ):
        tabs()

    assert capture.get() == "Select a choice: b\n"


def test_that_str_choices_are_rendered(tabs: Tabs):
    expected = """
    Select a choice:

    ←  a   b   c  →

    """

    assert_snapshot(tabs, expected)


def test_that_labels_and_descriptions_are_rendered():
    prompt = Tabs(
        "Select a choice:",
        [
            Choice("a", label="Choice A"),
            Choice("b", description="The second choice"),
            Choice("c", label="Choice C", description="The third choice"),
        ],
    )

    expected = """
    Select a choice:

    ←  Choice A   b   Choice C  →

    """

    assert_snapshot(prompt, expected)

    expected = """
    Select a choice:

    ←  Choice A   b   Choice C  →
    The second choice
    """

    assert_snapshot(prompt, expected, index=1)


def test_style():
    prompt = Tabs(
        "Select a choice:",
        [
            Choice("a", description="The first choice"),
            Choice("b", description="The second choice"),
            Choice("c", description="The third choice"),
        ],
    )

    expected = """
    [richer_prompt.title]Select a choice:[/]

    [richer_prompt.hint]←[/] [richer_prompt.tab.active] a [/]  b   c  →
    [richer_prompt.description]The first choice[/]
    """

    assert_snapshot(prompt, expected, raw=True)

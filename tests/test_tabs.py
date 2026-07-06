from unittest.mock import patch

import pytest
import readchar

from richer_prompt.choices import Choice
from richer_prompt.prompt.tabs import Tabs
from tests.utils import assert_snapshot, simulate


@pytest.fixture
def tabs(console) -> Tabs:
    return Tabs("Select a choice:", ["a", "b", "c"], console=console)


def test_that_choice_is_selected(tabs: Tabs):
    result = simulate(
        tabs,
        [
            readchar.key.RIGHT,
            readchar.key.TAB,
            readchar.key.LEFT,
            readchar.key.ENTER,
        ],
    )

    assert result == "b"


@pytest.mark.skipif(
    not hasattr(readchar.key, "SHIFT_TAB"), reason="SHIFT_TAB not supported in Windows"
)
def test_that_shift_tab_move_to_previous(tabs: Tabs):
    keys = [
        readchar.key.TAB,
        readchar.key.TAB,
        readchar.key.SHIFT_TAB,  # ty:ignore[unresolved-attribute]
        readchar.key.ENTER,
    ]

    assert simulate(tabs, keys) == "b"


@pytest.mark.parametrize(
    ("keys", "expected"),
    [
        ([readchar.key.LEFT, readchar.key.ENTER], "a"),
        (
            [
                readchar.key.RIGHT,
                readchar.key.RIGHT,
                readchar.key.RIGHT,
                readchar.key.ENTER,
            ],
            "c",
        ),
    ],
    ids=["left", "right"],
)
def test_that_cursor_doesnt_rollover(tabs: Tabs, keys, expected):
    assert simulate(tabs, keys) == expected


def test_that_cursor_starts_at_index(tabs: Tabs):
    assert simulate(tabs, [readchar.key.ENTER], index=1) == "b"


@pytest.mark.parametrize("index", [-1, 3])
def test_that_index_out_of_range_raises(tabs: Tabs, index):
    with pytest.raises(ValueError, match=f"Index '{index}' is out of range"):
        tabs(index=index)


def test_ask():
    with patch(
        "richer_prompt.session.readchar.readkey",
        side_effect=[readchar.key.RIGHT, readchar.key.ENTER],
    ):
        assert Tabs.ask("Select a choice:", ["a", "b", "c"], index=1) == "c"


def test_that_answer_is_rendered(tabs: Tabs):
    with tabs.console.capture() as capture:
        simulate(tabs, [readchar.key.RIGHT, readchar.key.ENTER])

    assert capture.get() == "Select a choice: b\n"


def test_that_str_choices_are_rendered(tabs: Tabs):
    widget = tabs._build_widget()

    expected = """
    Select a choice:

    ←  a   b   c  →

    """

    assert_snapshot(widget, expected)


def test_that_labels_and_descriptions_are_rendered():
    prompt = Tabs(
        "Select a choice:",
        [
            Choice("a", label="Choice A"),
            Choice("b", description="The second choice"),
            Choice("c", label="Choice C", description="The third choice"),
        ],
    )

    widget = prompt._build_widget()

    expected = """
    Select a choice:

    ←  Choice A   b   Choice C  →

    """

    assert_snapshot(widget, expected)

    widget = prompt._build_widget(index=1)

    expected = """
    Select a choice:

    ←  Choice A   b   Choice C  →
    The second choice
    """

    assert_snapshot(widget, expected)


def test_style():
    prompt = Tabs(
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

    [richer_prompt.description]←[/] [richer_prompt.tab.active] a [/]  b   c  →
    [richer_prompt.description]The first choice[/]
    """

    assert_snapshot(widget, expected, raw=True)

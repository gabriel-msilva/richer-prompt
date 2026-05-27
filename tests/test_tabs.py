from unittest.mock import patch

import pytest
import readchar

from richer_prompt.models import TabsSelectionModel
from richer_prompt.options import Option
from richer_prompt.prompt.tabs import Tabs
from tests.utils import assert_snapshot, simulate


@pytest.fixture
def tabs(console) -> Tabs:
    return Tabs("Select an option", ["a", "b", "c"], console=console)


def test_that_option_is_selected(tabs: Tabs):
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
        "richer_prompt.models.readchar.readkey",
        side_effect=[readchar.key.RIGHT, readchar.key.ENTER],
    ):
        assert Tabs.ask("Select an option", ["a", "b", "c"], index=1) == "c"


def test_that_answer_is_rendered(tabs: Tabs):
    with tabs.console.capture() as capture:
        simulate(tabs, [readchar.key.RIGHT, readchar.key.ENTER])

    assert capture.get() == "Select an option: b\n"


def test_that_str_options_are_rendered(tabs: Tabs):
    model = TabsSelectionModel(tabs.options)

    expected = """
    Select an option:

    ←  a   b   c  →

    """

    assert_snapshot(tabs, model, expected)


def test_that_labels_and_descriptions_are_rendered():
    prompt = Tabs(
        "Select an option",
        [
            Option("a", label="Option A"),
            Option("b", description="The second option"),
            Option("c", label="Option C", description="The third option"),
        ],
    )

    model = TabsSelectionModel(prompt.options)

    expected = """
    Select an option:

    ←  Option A   b   Option C  →

    """

    assert_snapshot(prompt, model, expected)

    model = TabsSelectionModel(prompt.options, cursor=1)

    expected = """
    Select an option:

    ←  Option A   b   Option C  →
    The second option
    """

    assert_snapshot(prompt, model, expected)


def test_style():
    prompt = Tabs(
        "Select an option",
        [
            Option("a", description="The first option"),
            Option("b", description="The second option"),
            Option("c", description="The third option"),
        ],
    )

    model = TabsSelectionModel(prompt.options)

    expected = """
    [richer_prompt.title]Select an option:[/]

    [richer_prompt.description]←[/] [richer_prompt.tab.active] a [/]  b   c  →
    [richer_prompt.description]The first option[/]
    """

    assert_snapshot(prompt, model, expected, raw=True)

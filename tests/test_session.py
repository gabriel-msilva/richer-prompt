from unittest.mock import patch

import pytest
import readchar

from richer_prompt import NotInteractiveError, Select
from richer_prompt.session import _eof_keys
from tests.utils import simulate


@pytest.fixture
def select(console) -> Select:
    return Select("Pick:", ["a", "b"], console=console)


def test_that_non_tty_stdin_raises(select: Select):
    with patch("sys.stdin") as stdin:
        stdin.isatty.return_value = False

        with pytest.raises(NotInteractiveError, match="interactive terminal"):
            select()


def test_that_missing_stdin_raises(select: Select):
    with (
        patch("sys.stdin", None),
        pytest.raises(NotInteractiveError, match="interactive terminal"),
    ):
        select()


def test_that_injected_read_key_skips_the_tty_check(select: Select):
    assert simulate(select, [readchar.key.ENTER]) == "a"


def test_that_ctrl_d_raises_eof_error(select: Select):
    with pytest.raises(EOFError):
        simulate(select, [readchar.key.DOWN, readchar.key.CTRL_D])


@pytest.mark.parametrize(
    ("platform", "expected"),
    [
        ("linux", {readchar.key.CTRL_D}),
        ("darwin", {readchar.key.CTRL_D}),
        ("win32", {readchar.key.CTRL_D, readchar.key.CTRL_Z}),
    ],
)
def test_that_eof_keys_match_the_platform_convention(platform, expected):
    assert _eof_keys(platform) == expected


def test_that_ctrl_c_propagates(select: Select):
    with pytest.raises(KeyboardInterrupt):
        simulate(select, [readchar.key.DOWN, KeyboardInterrupt()])


def test_that_no_answer_is_rendered_on_cancel(select: Select):
    with select.console.capture() as capture, pytest.raises(EOFError):
        simulate(select, [readchar.key.CTRL_D])

    assert capture.get() == ""

from unittest.mock import patch

import pytest

from richer_prompt import NotInteractiveError, Select, keys
from richer_prompt.testing import simulate_keys


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


def test_that_simulated_keys_skip_the_tty_check(select: Select):
    with simulate_keys([keys.ENTER]):
        assert select() == "a"


def test_that_ctrl_d_raises_eof_error(select: Select):
    with (
        simulate_keys([keys.DOWN, keys.CTRL_D]),
        pytest.raises(EOFError),
    ):
        select()


def test_that_ctrl_c_propagates(select: Select):
    with (
        simulate_keys([keys.DOWN, keys.CTRL_C]),
        pytest.raises(KeyboardInterrupt),
    ):
        select()


def test_that_no_answer_is_rendered_on_cancel(select: Select):
    with (
        select.console.capture() as capture,
        simulate_keys([keys.CTRL_D]),
        pytest.raises(EOFError),
    ):
        select()

    assert capture.get() == ""

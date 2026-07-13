from unittest.mock import patch

import pytest

from richer_prompt import NotInteractiveError, Select, keys
from richer_prompt.testing import simulate_keys


@pytest.fixture
def select(console) -> Select:
    return Select("Pick:", ["a", "b"], console=console)


def test_that_prompts_read_the_simulated_keys(select: Select):
    with simulate_keys(keys.DOWN, keys.ENTER):
        assert select() == "b"


def test_that_ask_reads_the_simulated_keys(console):
    def pick() -> str:
        return Select.ask("Pick:", ["a", "b"], console=console)

    with simulate_keys(keys.DOWN, keys.ENTER):
        assert pick() == "b"


def test_that_one_block_spans_multiple_prompts(select: Select):
    with simulate_keys(keys.ENTER, keys.DOWN, keys.ENTER):
        assert select() == "a"
        assert select() == "b"


def test_that_exhausted_keys_raise(select: Select):
    with (
        simulate_keys(keys.DOWN),
        pytest.raises(AssertionError, match="ran out of simulated keys"),
    ):
        select()


def test_that_simulation_ends_with_the_block(select: Select):
    with simulate_keys(keys.ENTER):
        select()

    with patch("sys.stdin") as stdin:
        stdin.isatty.return_value = False

        with pytest.raises(NotInteractiveError):
            select()

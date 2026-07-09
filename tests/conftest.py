import pytest
from rich.console import Console

pytest.register_assert_rewrite("tests.utils")


@pytest.fixture(scope="session")
def console() -> Console:
    return Console(width=60, height=40, color_system=None, force_terminal=False)

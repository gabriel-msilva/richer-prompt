import contextlib
from collections.abc import Callable, Iterator, Sequence

from richer_prompt.keys import CTRL_C
from richer_prompt.session import _key_source_override

__all__ = ["simulate_keys"]


@contextlib.contextmanager
def simulate_keys(*keys: str) -> Iterator[None]:
    """
    Simulate keyboard input for prompts run within the context block.

    Prompts read the given keys in order instead of the real keyboard,
    so no interactive terminal is required.

    .. versionadded:: 0.2.0

    Parameters
    ----------
    *keys: str
        The keys to deliver, e.g. :py:data:`richer_prompt.keys.DOWN` or plain
        characters. Control keys behave like the real keyboard:
        ``richer_prompt.keys.CTRL_C`` raises ``KeyboardInterrupt`` and
        ``richer_prompt.keys.CTRL_D`` raises ``EOFError``.

    Raises
    ------
    AssertionError
        If a prompt is still waiting for input after all keys were delivered.

    Examples
    --------
    >>> from richer_prompt import keys, Select
    >>> from richer_prompt.testing import simulate_keys
    >>> with simulate_keys(keys.DOWN, keys.ENTER):
    ...     Select.ask("Choose a color:", ["Red", "Green", "Blue"])
    'Green'
    """
    token = _key_source_override.set(_scripted_reader(keys))

    try:
        yield
    finally:
        _key_source_override.reset(token)


def _scripted_reader(keys: Sequence[str]) -> Callable[[], str]:
    remaining = iter(keys)

    def read_key() -> str:
        try:
            key = next(remaining)
        except StopIteration:
            raise AssertionError(
                "ran out of simulated keys, but the prompt is still waiting for input"
            ) from None

        # mirror how the real key source surfaces Ctrl+C
        if key == CTRL_C:
            raise KeyboardInterrupt

        return key

    return read_key

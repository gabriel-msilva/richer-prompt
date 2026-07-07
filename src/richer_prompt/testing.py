import contextlib
from collections.abc import Callable, Iterator, Sequence

import readchar

from richer_prompt.session import _key_source_override

__all__ = ["simulate_keys"]


@contextlib.contextmanager
def simulate_keys(keys: Sequence[str]) -> Iterator[None]:
    """
    Simulate keyboard input for prompts run within the context block.

    Prompts read the given keys in order instead of the real keyboard,
    so no interactive terminal is required.

    .. versionadded:: 0.2.0

    Parameters
    ----------
    keys: sequence of str
        The keys to deliver, e.g. :py:data:`readchar.key.DOWN` or plain characters.
        Control keys behave like the real keyboard: ``readchar.key.CTRL_C``
        raises ``KeyboardInterrupt`` and ``readchar.key.CTRL_D`` raises
        ``EOFError``.

    Raises
    ------
    AssertionError
        If a prompt is still waiting for input after all keys were delivered.

    Examples
    --------
    >>> import readchar
    >>> from richer_prompt import Select
    >>> from richer_prompt.testing import simulate_keys
    >>> with simulate_keys([readchar.key.DOWN, readchar.key.ENTER]):
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

        # what readchar.readkey() does with Ctrl+C
        if key == readchar.key.CTRL_C:
            raise KeyboardInterrupt

        return key

    return read_key

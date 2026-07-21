Testing
=======

.. currentmodule:: richer_prompt

Use :py:func:`richer_prompt.testing.simulate_keys` to test code that runs prompts.
Prompts inside the block read the given keys instead of the real keyboard,
so no interactive terminal is required.

.. code-block:: python

    from richer_prompt import keys, Select
    from richer_prompt.testing import simulate_keys

    select_color = Select("Choose a color:", ["Red", "Green", "Blue"])

    with simulate_keys(keys.DOWN, keys.ENTER):
        assert select_color() == "Green"

If the keys run out while a prompt is still waiting for input, the key read raises :py:exc:`AssertionError`.
Control keys behave like the real keyboard, for example,
``keys.CTRL_C`` raises :py:exc:`KeyboardInterrupt` and ``keys.CTRL_D`` raises :py:exc:`EOFError`.

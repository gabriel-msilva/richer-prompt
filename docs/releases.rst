Release notes
=============

.. currentmodule:: richer_prompt

Version 0.2.0 (unreleased)
--------------------------

API changes
~~~~~~~~~~~

- Added :py:func:`richer_prompt.testing.simulate_keys` to simulate keyboard input when testing code that runs prompts.

Fixes
~~~~~

- Removed unused ``richer_prompt.cursor.submit`` and ``richer_prompt.choice.description`` style names from the docs.
- Importing ``richer_prompt`` no longer touches ``rich`` global state, and styling now resolves at prompt time.
- Prompts raise :py:exc:`NotInteractiveError` when standard input is not an interactive terminal,
  instead of crashing with a cryptic ``termios`` error.
- :kbd:`Ctrl+C` raises :py:exc:`KeyboardInterrupt` and :kbd:`Ctrl+D` (or :kbd:`Ctrl+Z` on Windows)
  raises :py:exc:`EOFError` while a prompt is running.

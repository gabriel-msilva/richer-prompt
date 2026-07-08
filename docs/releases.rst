Release notes
=============

.. currentmodule:: richer_prompt

Version 0.2.0 (unreleased)
--------------------------

Build changes
~~~~~~~~~~~~~

- Switched keyboard input from ``readchar`` to ``blessed``, which resolves key sequences across
  more terminals (e.g. every :kbd:`Home`/:kbd:`End` and :kbd:`Shift+Tab` variant).

API changes
~~~~~~~~~~~

- Added :py:func:`richer_prompt.testing.simulate_keys` to simulate keyboard input when testing code that runs prompts.
- Added the :py:mod:`richer_prompt.keys` module of key tokens (e.g. ``keys.DOWN``, ``keys.ENTER``)
  to pass to :py:func:`richer_prompt.testing.simulate_keys`.
- The ``numbered`` option of :py:class:`Select` and :py:class:`MultiSelect` now defaults to ``None``,
  which displays choice numbers only when the prompt has at most 9 choices, so every displayed number works as a digit shortcut.
  Pass ``True`` or ``False`` to force numbers (and their digit shortcuts) on or off.

Fixes
~~~~~

- Removed unused ``richer_prompt.cursor.submit`` and ``richer_prompt.choice.description`` style names from the docs.
- Importing ``richer_prompt`` no longer touches ``rich`` global state, and styling now resolves at prompt time.
- Prompts raise :py:exc:`NotInteractiveError` when standard input is not an interactive terminal,
  instead of crashing with a cryptic ``termios`` error.
- :kbd:`Ctrl+C` raises :py:exc:`KeyboardInterrupt` and :kbd:`Ctrl+D` (or :kbd:`Ctrl+Z` on Windows)
  raises :py:exc:`EOFError` while a prompt is running.

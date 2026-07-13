Release notes
=============

.. currentmodule:: richer_prompt

Version 0.2.0 (unreleased)
--------------------------

Build changes
~~~~~~~~~~~~~

- Switched keyboard input from ``readchar`` to ``blessed``, which resolves key sequences
  across more terminals.

API changes
~~~~~~~~~~~

- Added ``viewport_size`` parameter to :py:class:`Select` and :py:class:`MultiSelect`
  to cap the number of choices visible at once (at least 3).
  By default, prompts fit as many choices as the terminal height allows.
- The ``numbered`` parameter of :py:class:`Select` and :py:class:`MultiSelect` now defaults to ``None``,
  which shows numbers only when the prompt has at most 9 choices and they all fit in the viewport.
  Pass ``True`` or ``False`` to force numbers (and digit shortcuts) on or off.
- Added :py:func:`richer_prompt.testing.simulate_keys` to simulate keyboard input when testing code that runs prompts.
- Added the :py:mod:`richer_prompt.keys` module of key tokens (e.g. ``keys.DOWN``, ``keys.ENTER``)
  to pass to :py:func:`richer_prompt.testing.simulate_keys`.
- Added support for `vim` key bindings and :kbd:`Home`/:kbd:`End` keys to jump to the first/last row of a prompt.

Fixes
~~~~~

- Importing ``richer_prompt`` no longer touches ``rich`` global state, and styling now resolves at prompt time.
- Prompts raise :py:exc:`NotInteractiveError` when standard input is not an interactive terminal,
  instead of crashing with a cryptic ``termios`` error.
- :kbd:`Ctrl+C` raises :py:exc:`KeyboardInterrupt` and :kbd:`Ctrl+D` (or :kbd:`Ctrl+Z` on Windows)
  raises :py:exc:`EOFError` while a prompt is running.
- Removed unused style names from the docs.

Interactivity
=============

.. currentmodule:: richer_prompt

Prompts read single keystrokes, so they require an interactive terminal.
When standard input is not a TTY (for example a pipe or a CI job),
prompts raise :py:exc:`NotInteractiveError` before rendering anything.

Keybindings
-----------

- Arrow keys (or vi-like keybindings :kbd:`k`, :kbd:`j`, etc) to move the cursor.
- :kbd:`Home`/:kbd:`End` jump to the first/last option.
- :kbd:`Tab`/:kbd:`Shift+Tab` to switch tabs in :py:class:`Tabs` and :py:class:`Form`.

Interrupts
----------

While a prompt is running:

- :kbd:`Ctrl+C` raises :py:exc:`KeyboardInterrupt`.
- :kbd:`Ctrl+D` (or :kbd:`Ctrl+Z` on Windows) raises :py:exc:`EOFError`.

Handle both as you would for any other :py:func:`input` call.

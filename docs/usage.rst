Usage
=====

*rich-prompt* provides interactive terminal prompts.
Users can navigate and select from a list of options.

All prompt classes follow the same API of
`rich.prompt.Prompt <https://rich.readthedocs.io/en/stable/prompt.html>`_.

Prompts
-------

Call the instance for a reusable prompt, or use the ``.ask()`` class method for a one-off prompt.

.. code-block:: python

    from richer_prompt import Select

    # Reusable prompt instance
    select_prompt = Select("Select a color:", choices=["Red", "Green", "Blue"])
    choice = select_prompt()

    # One-off prompt
    choice = Select.ask("Select a color:", choices=["Red", "Green", "Blue"])

.. snapshot::
    :hide-code:

    Select.ask("Select a color:", choices=["Red", "Green", "Blue"])

The prompt message may be given as a string
(which may contain `Console Markup <https://rich.readthedocs.io/en/stable/markup.html#console-markup>`_ and emoji code)
or as a :py:class:`rich.text.Text` instance.

.. snapshot::

    Select.ask("[cyan]?[/cyan] Select a [i]color[/i]:", choices=["Red", "Green", "Blue"])

See the :ref:`api` for details on each prompt class and their available options.

Choices
-------

Use :py:class:`Choice` objects in the `choices` list for more control over the display and formatting.

- :py:attr:`Choice.value` is the actual value returned when the choice is selected (can be any type that implements ``__str__``).
- :py:attr:`Choice.label` replaces the text in the prompt display. (optional)
- :py:attr:`Choice.description` adds secondary text to the choice. (optional)

.. snapshot::

    from richer_prompt import Choice, Tabs

    Tabs.ask(
        "Do you want to continue?",
        choices=[
            Choice(False, label="No", description="Cancel and exit"),
            Choice(True, label="Yes", description="This action cannot be undone"),
        ]
    )

Themes
------

Prompts are styled with Rich themes.
When a prompt runs, any ``richer_prompt.*`` style defined in the console's theme
overrides the default style; all other style names fall back to the defaults
listed below, no matter when the theme was created.

.. snapshot::

    from rich.console import Console
    from rich.theme import Theme

    from richer_prompt import MultiSelect

    theme = Theme({"richer_prompt.cursor": "blue bold", "richer_prompt.hint": "yellow italic"})
    console = Console(theme=theme)

    MultiSelect.ask(
        "Select multiple options:",
        choices=["Option 1", "Option 2", "Option 3"],
        console=console
    )


The following style names are available for customization:

.. list-table:: richer-prompt style names
        :header-rows: 1
        :widths: 35 20 45

        * - Style name
          - Default style
          - Description
        * - ``richer_prompt.title``
          - ``bold``
          - Prompt title text.
        * - ``richer_prompt.description``
          - ``dim``
          - Prompt description text displayed under the title.
        * - ``richer_prompt.hint``
          - ``dim``
          - Hint text shown at the bottom of prompts.
        * - ``richer_prompt.choice``
          - `null`
          - Base style for choice labels.
        * - ``richer_prompt.cursor``
          - ``magenta``
          - Active cursor indicator for the current option.
        * - ``richer_prompt.checkbox``
          - `null`
          - Base style for checkbox markers in multiselect prompts.
        * - ``richer_prompt.checkbox.checked``
          - ``green``
          - Checkbox marker style for selected items.
        * - ``richer_prompt.tab``
          - `null`
          - Base style for tab labels.
        * - ``richer_prompt.tab.active``
          - ``magenta reverse``
          - Style for the currently active tab.

Interactivity and cancellation
------------------------------

Prompts read single keystrokes, so they require an interactive terminal.
When standard input is not a TTY (for example a pipe or a CI job),
prompts raise :py:exc:`richer_prompt.NotInteractiveError` before rendering anything.

While a prompt is running:

- :kbd:`Ctrl+C` raises :py:exc:`KeyboardInterrupt`.
- :kbd:`Ctrl+D` (or :kbd:`Ctrl+Z` on Windows) raises :py:exc:`EOFError`.

Handle both as you would for any other :py:func:`input` call.

Testing
-------

Use :py:func:`richer_prompt.testing.simulate_keys` to test code that runs prompts.
Prompts inside the block read the given keys instead of the real keyboard,
so no interactive terminal is required.

.. code-block:: python

    import readchar

    from richer_prompt import Select
    from richer_prompt.testing import simulate_keys


    def pick_color() -> str:
        return Select.ask("Choose a color:", ["Red", "Green", "Blue"])


    def test_pick_color():
        with simulate_keys([readchar.key.DOWN, readchar.key.ENTER]):
            assert pick_color() == "Green"

If the keys run out while a prompt is still waiting for input,
the key read raises :py:exc:`AssertionError`.
Control keys behave like the real keyboard:
``readchar.key.CTRL_C`` raises :py:exc:`KeyboardInterrupt`
and ``readchar.key.CTRL_D`` raises :py:exc:`EOFError`.

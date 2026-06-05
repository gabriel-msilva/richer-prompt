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

`richer-prompt` injects extra styles to the default Rich theme,
so you can customize the appearance of prompts with Rich themes.

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
        * - ``richer_prompt.choice.description``
          - ``dim``
          - Secondary text shown next to each choice.
        * - ``richer_prompt.cursor``
          - ``light_steel_blue``
          - Active cursor indicator for the current option.
        * - ``richer_prompt.cursor.submit``
          - ``bold``
          - Cursor indicator when focused on the submit row.
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
          - ``light_steel_blue reverse``
          - Style for the currently active tab.

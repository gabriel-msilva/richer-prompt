Theming
=======

.. currentmodule:: richer_prompt

Prompts are styled with Rich themes.
When a prompt runs, any ``richer_prompt.*`` style defined in the console's theme
overrides the default style; all other style names fall back to the defaults
listed below, no matter when the theme was created.

.. snapshot::

    from rich.console import Console
    from rich.style import Style
    from rich.theme import Theme

    from richer_prompt import MultiSelect

    theme = Theme(
        {
            "richer_prompt.title": "",  # or Style.null() for no style
            "richer_prompt.cursor": "blue bold",
            "richer_prompt.hint": Style(color="yellow", italic=True),
        }
    )

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
        * - ``richer_prompt.selected``
          - ``green``
          - Style for selected choice labels or checkboxes.
        * - ``richer_prompt.disabled``
          - ``dim``
          - Style for choices marked as disabled (unselectable).
        * - ``richer_prompt.tab``
          - `null`
          - Base style for tab labels.
        * - ``richer_prompt.tab.active``
          - ``magenta reverse``
          - Style for the currently active tab.
        * - ``richer_prompt.warning``
          - ``yellow``
          - Style for warning messages shown by prompts.

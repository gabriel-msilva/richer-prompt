Prompts
=======

.. currentmodule:: richer_prompt

`richer-prompt` provides several interactive terminal prompts.
Users can navigate and select from a list of options with the keyboard.

All prompt classes share the same API as
`rich.prompt.Prompt <https://rich.readthedocs.io/en/stable/prompt.html>`_.

Call the instance for a reusable prompt, or use the ``.ask()`` class method for a one-off prompt.

.. code-block:: python

    from richer_prompt import Select

    # Reusable prompt instance
    prompt = Select("Select a color:", choices=["Red", "Green", "Blue"])
    answer = prompt()

    # One-off prompt
    answer = Select.ask("Select a color:", choices=["Red", "Green", "Blue"])

The prompt message may be given as a string
(which may contain `Console Markup <https://rich.readthedocs.io/en/stable/markup.html#console-markup>`_ and emoji code)
or as a :py:class:`rich.text.Text` instance.

.. snapshot::

    Select.ask("[cyan]?[/cyan] Select a [i]color[/i]:", choices=["Red", "Green", "Blue"])

.. seealso:: :ref:`api` for the full list of options on each class.

Select
------

:py:class:`Select` asks the user to pick a single option from a list.

The ``numbered`` parameter controls digit shortcuts.
By default, it shows numbers only when there are at most 9 choices and they all fit in the viewport.

Use ``viewport_size`` to cap how many choices are visible at once (at least 3);
by default the prompt fits as many choices as the terminal height allows.

.. snapshot::

    Select.ask(
        "Choose a license:",
        choices=[
            "Apache License 2.0",
            "GNU General Public License v3.0",
            "MIT License",
            "BSD 2-Clause License",
            "BSD 3-Clause License"
        ],
        viewport_size=4,
    )


MultiSelect
-----------

:py:class:`MultiSelect` lets the user select multiple options.
It shares ``viewport_size`` and ``numbered`` with :py:class:`Select`,
and also accepts a ``default`` set of preselected choices.

.. snapshot::

    from richer_prompt import MultiSelect

    MultiSelect.ask(
        "Which languages do you speak?",
        choices=["English", "Spanish", "Portuguese", "Chinese"],
        default={0},
    )

Tabs
----

:py:class:`Tabs` presents a small set of options as a horizontal, tabbed selector.
Use :kbd:`Tab`/:kbd:`Shift+Tab` in addition to the arrow keys to switch between tabs.

.. snapshot::

    from richer_prompt import Tabs

    Tabs.ask("Do you want to continue?", choices=["No", "Yes"])

Form
----

:py:class:`Form` asks a sequence of :py:class:`Select` or :py:class:`MultiSelect` prompts
as a single, navigable form, returning all answers together.

It takes a dictionary of steps where each key is a label and each value is a prompt instance.
Names are used as labels for each prompt.

.. snapshot::

    from richer_prompt import Form, Select, MultiSelect

    Form.ask(
        {
            "OS": Select(
                "What is your operating system?",
                choices=["Linux", "Windows", "macOS"]
            ),
            "Languages": MultiSelect(
                "What programming languages do you use?",
                choices=["Python", "C++", "Rust", "Go"]
            ),
        }
    )

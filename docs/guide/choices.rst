Choices
=======

.. currentmodule:: richer_prompt

Use :py:class:`Choice` objects in the ``choices`` list for more control over the display and formatting.

- :py:attr:`Choice.value` is the actual value returned when the choice is selected.
  If ``label`` is not set, the object must implement ``__str__`` method.
- :py:attr:`Choice.label` replaces the text in the prompt display. (optional)
- :py:attr:`Choice.description` adds secondary text to the choice. (optional)

.. snapshot::

    from richer_prompt import Choice, Select

    Select.ask(
        "Do you want to continue?",
        choices=[
            Choice(value=False, label="No", description="Abort and exit"),
            Choice(value=True, label="Yes", description="This action cannot be undone"),
        ]
    )


Pass ``disabled=True`` to mark a choice as unselectable.

.. snapshot::

    from richer_prompt import Choice, Select

    Select.ask(
        "Choose a plan tier:",
        choices=[
            "Free",
            "Pro",
            Choice("Enterprise", description="Consulting required", disabled=True),
        ]
    )

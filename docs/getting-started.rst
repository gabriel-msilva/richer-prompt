Getting started
===============

Installation
------------

You can install `richer-prompt` from PyPI with pip or your favorite package manager:

.. tab:: pip

   .. code-block:: bash

      pip install richer-prompt

.. tab:: uv

   .. code-block:: bash

      uv add richer-prompt

Demo
----

To check if `richer-prompt` was installed correctly, and to see a quick demo of its capabilities,
run the following from the command line:

.. code-block:: bash

   python -m richer_prompt

.. image:: assets/demo.gif
   :alt: richer-prompt demo
   :align: center

Quickstart
----------

Every prompt follows the same API as
`rich.prompt.Prompt <https://rich.readthedocs.io/en/stable/prompt.html>`_.
Call an instance for a reusable prompt, or use the ``.ask()`` class method for a one-off prompt.

.. code-block:: python

    from richer_prompt import Select

    # Reusable prompt instance
    prompt = Select("Select a color:", choices=["Red", "Green", "Blue"])
    answer = prompt()

    # One-off prompt
    answer = Select.ask("Select a color:", choices=["Red", "Green", "Blue"])

.. snapshot::
    :hide-code:

    Select.ask("Select a color:", choices=["Red", "Green", "Blue"])

See more examples and other prompt types in :doc:`guide/prompts`,
or jump to the :ref:`api` for the full reference.

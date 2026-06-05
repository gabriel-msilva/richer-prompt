richer-prompt
=============

richer-prompt provides interactive terminal prompts built on top of `Rich <https://github.com/Textualize/rich>`_.

**Version**: |release|

**Useful links**:
`Source Repository <https://github.com/gabriel-msilva/richer-prompt>`_
| `Issues & Ideas <https://github.com/gabriel-msilva/richer-prompt/issues>`_


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

To check if `richer-prompt` was installed correctly, and to see a little of what it can do,
run the following from the command line:

.. code-block:: bash

   python -m richer_prompt


.. snapshot::
   :hide-code:
   :title: richer-prompt

   Select.ask(
      "Choose a bread:",
      [
         Choice("white", label="White", description="Soft and fluffy"),
         Choice("whole_wheat", label="Whole wheat", description="Nutty and hearty"),
         Choice("sourdough", label="Sourdough", description="Tangy and crusty"),
      ],
   )

.. toctree::
   :maxdepth: 2
   :caption: Contents

   usage
   api

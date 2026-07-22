.. _api:

API Reference
=============

.. currentmodule:: richer_prompt

Prompts
-------

.. autoclass:: richer_prompt.Select
   :members:
   :inherited-members:
   :special-members: __call__

.. autoclass:: richer_prompt.MultiSelect
   :members:
   :inherited-members:
   :special-members: __call__

.. autoclass:: richer_prompt.Tabs
   :members:
   :inherited-members:
   :special-members: __call__

.. autoclass:: richer_prompt.Form
   :members:
   :inherited-members:
   :special-members: __call__

Choices
-------

.. autoclass:: richer_prompt.Choice
   :members:

Exceptions
----------

.. autoexception:: richer_prompt.NotInteractiveError

.. autoexception:: richer_prompt.PromptCancelled

Keys
----

.. automodule:: richer_prompt.keys
   :members:

Testing
-------

.. autofunction:: richer_prompt.testing.simulate_keys

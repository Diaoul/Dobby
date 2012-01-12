Triggers
========

Triggers are used to trigger events when an audio input is received.

Base
----

Trigger
^^^^^^^
.. autoclass:: dobby.triggers.Trigger
    :members:

Events
^^^^^^
Events are raised by triggers to communicate
 
.. autoclass:: dobby.triggers.ActionEvent
    :members:
.. autoclass:: dobby.triggers.RecognitionEvent
    :members:

Clapper
-------

The Clapper is used to match a :class:`~dobby.triggers.clapper.Sequence` of :class:`Blocks <dobby.triggers.clapper.Block>`.
The :class:`~dobby.triggers.clapper.Pattern` is composed of :class:`PatternItems <dobby.triggers.clapper.PatternItem>` that will validates
or not, depending on its parameters, a specific kind of :class:`~dobby.triggers.clapper.Block`. 

Sequence
^^^^^^^^
.. autoclass:: dobby.triggers.clapper.Sequence
    :members:
    :show-inheritance:
.. autoclass:: dobby.triggers.clapper.Block
    :members:
.. autoclass:: dobby.triggers.clapper.QuietBlock
    :show-inheritance:
.. autoclass:: dobby.triggers.clapper.NoisyBlock
    :show-inheritance:

Pattern
^^^^^^^
.. autoclass:: dobby.triggers.clapper.Pattern
    :members:
.. autoclass:: dobby.triggers.clapper.PatternItem
    :members:
.. autoclass:: dobby.triggers.clapper.QuietPattern
    :show-inheritance:
.. autoclass:: dobby.triggers.clapper.NoisyPattern
    :show-inheritance:

Clapper
^^^^^^^
.. autoclass:: dobby.triggers.clapper.Clapper
    :members:
    :show-inheritance:

Julius
------
.. automodule:: dobby.triggers.julius
    :members:
    :show-inheritance:
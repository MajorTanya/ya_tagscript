==========
Interfaces
==========

.. module:: ya_tagscript.interfaces
    :synopsis: Interfaces used by the library

These are the interfaces / abstract base classes (:class:`abc.ABC`) used across the
project. Generally, where Adapters/Blocks/Interpreters/Nodes are interacted with, these
ABCs are used as the interface.

For example, the concrete :class:`~ya_tagscript.interpreter.TagScriptInterpreter`
(itself a subclass of :class:`InterpreterABC`) gets passed a sequence of
:class:`BlockABC` on instantiation and does not "know about" any concrete blocks like
:class:`~ya_tagscript.blocks.MathBlock`.

.. autoclass:: AdapterABC
    :members:
    :no-show-inheritance:

.. autoclass:: BlockABC
    :members:
    :private-members: _accepted_names
    :no-show-inheritance:

.. autoclass:: InterpreterABC
    :members:
    :no-show-inheritance:
    :special-members: __init__

.. autoclass:: NodeABC
    :members:
    :no-show-inheritance:
    :special-members: __init__

.. autoenum:: NodeType
    :no-show-inheritance:

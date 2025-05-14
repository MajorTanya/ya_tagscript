========
Adapters
========

These adapters are used to supply data to a TagScript script, most prominently when
using the ``seed_variables`` parameter to provide seed variables to the
:meth:`~ya_tagscript.interfaces.InterpreterABC.process` method of a given interpreter
instance. These adapters are also used internally when a script contains a
:class:`~ya_tagscript.blocks.AssignmentBlock`.

Their stored values are accessed through variable blocks in TagScript.

.. literalinclude:: code_examples/adapters/int_adapter_example.py
    :caption: Example: How to use an IntAdapter
    :language: Python
    :linenos:

Reference
=========

.. module:: ya_tagscript.adapters
    :synopsis: Adapters for supplying external data to the interpreter

Basic adapters
--------------

These adapters are used to provide simple values to the interpreter.

.. autoclass:: IntAdapter

.. autoclass:: FunctionAdapter

.. autoclass:: ObjectAdapter

.. autoclass:: StringAdapter

Discord adapters
----------------

These adapters connect the more complex Discord-specific types to the interpreter, e.g.
:class:`discord.Member`.

.. autoclass:: AttributeAdapter

.. autoclass:: ChannelAdapter

.. autoclass:: GuildAdapter

.. autoclass:: MemberAdapter

Example
=======

Using an adapter for a :class:`discord.Member` in a tiny Discord bot [#]_

For this example, assume the invoking user has the ID 123.

.. literalinclude:: code_examples/adapters/member_adapter_example.py
    :caption: Using a MemberAdapter with a discord.py bot
    :language: Python
    :linenos:
    :emphasize-lines: 4,11-15,24-28

.. rubric:: Footnotes
.. [#] This bot example was adapted from `discord.py's documentation <dpy_example_>`_

.. _dpy_example: https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html#commands

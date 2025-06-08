======
Blocks
======

.. module:: ya_tagscript.blocks
    :synopsis: Available blocks

Blocks are the core concept of TagScript. Each block encapsulates a specific behaviour,
like the :class:`CaseBlock`, which can transform input text to UPPERCASE or lowercase.

----

Action Blocks
=============

A group of blocks that can be used to signal some sort of action to be taken by the
client. Characterised by adding data to the the
:attr:`~ya_tagscript.interpreter.Response.actions` attribute of the Interpreter's
:class:`~ya_tagscript.interpreter.Response` return value.

.. autoclass:: CommandBlock

.. autoclass:: DeleteBlock

.. autoclass:: OverrideBlock

.. autoclass:: ReactBlock

.. autoclass:: RedirectBlock

.. autoclass:: SilenceBlock

----

Conditional Blocks
==================

.. autoclass:: AllBlock

.. autoclass:: AnyBlock

.. autoclass:: IfBlock

----

Discord Blocks
==============

.. autoclass:: CooldownBlock

.. autoclass:: EmbedBlock

----

Flow Blocks
===========

.. autoclass:: BreakBlock

.. autoclass:: ShortcutRedirectBlock

.. autoclass:: StopBlock

----

Limiter Blocks
==============

.. autoclass:: BlacklistBlock

.. autoclass:: RequireBlock

----

List Blocks
===========

.. autoclass:: CycleBlock

.. autoclass:: ListBlock

----

Math Blocks
===========

.. autoclass:: MathBlock

.. autoclass:: OrdinalBlock

----

Meta Blocks
===========

.. autoclass:: CommentBlock

.. autoclass:: DebugBlock

----

RNG Blocks
==========

.. autoclass:: FiftyFiftyBlock

.. autoclass:: RandomBlock

.. autoclass:: RangeBlock

----

String Blocks
=============

.. autoclass:: CaseBlock

.. autoclass:: JoinBlock

.. autoclass:: PythonBlock

.. autoclass:: ReplaceBlock

.. autoclass:: SubstringBlock

.. autoclass:: URLDecodeBlock

.. autoclass:: URLEncodeBlock

----

Time Blocks
===========

.. autoclass:: StrfBlock

.. autoclass:: TimedeltaBlock
    :special-members: __init__

----

Variable Blocks
===============

.. autoclass:: AssignmentBlock

.. autoclass:: LooseVariableGetterBlock
    :members: will_accept

.. autoclass:: StrictVariableGetterBlock
    :members: will_accept

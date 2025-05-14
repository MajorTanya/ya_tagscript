=========================
Introduction to TagScript
=========================

Anatomy of a TagScript Block
============================

In scripts, TagScript blocks are always written surrounded by curly braces (``{`` and
``}``). A TagScript block consists of three sections::

    {declaration(parameter):payload}

The ``declaration`` is mandatory for all blocks and communicates which block should be
used to process a given segment of TagScript. Some blocks may only consist of a
declaration.

The ``parameter`` *can* be mandatory OR optional, depending on the block being used.
*If present*, it is always enclosed in parentheses (``(`` and ``)``) and immediately
follows the ``declaration``.

Some blocks *require* some sort of parameter to be passed, others *can* work with a
parameter being passed but don't need it. For those blocks with optional parameters,
behaviour will often differ between their no-parameter and parameter-passed forms.

Whether a block requires a parameter or not is noted in the specific block's
documentation.

The ``payload`` *can* be mandatory OR optional, depending on the block being used (just
like the ``parameter``). *If present*, it is always preceded by a colon (``:``). The
colon either comes immediately after the ``declaration`` (if no ``parameter`` is used)
or immediately after the closing parenthesis of the parameter.

Whether a block requires a payload or not is noted in the specific block's
documentation.

If any of the sections violate their positioning rules in any way, the entire segment
is rejected and returned as-is, without further interpretation happening.

Valid Block Structures
----------------------

Given the above mentioned combinations, these are the only possible valid block
structures::

    {declaration}
    {declaration(parameter)}
    {declaration:payload}
    {declaration(parameter):payload}

Examples for each combination:

    #. ``{declaration}`` — :class:`~ya_tagscript.blocks.SilenceBlock`
    #. ``{declaration(parameter)}`` — :class:`~ya_tagscript.blocks.RedirectBlock`
    #. ``{declaration:payload}`` — :class:`~ya_tagscript.blocks.CaseBlock`
    #. ``{declaration(parameter):payload}`` — :class:`~ya_tagscript.blocks.IfBlock`

Click on their names to see their documentation and some examples.

Nesting Blocks
==============

It is possible to nest TagScript blocks within one another. Specifically, any one block
section may be nested deeper but nesting must not cross between sections. This means
that a block's ``declaration``, ``parameter``, and ``payload`` may all be deeply nested
blocks themselves, but they cannot be combined. A nested block cannot provide both the
``parameter`` AND the ``payload`` at the same time. Separately nested blocks are
required in order to uphold the fundamental structure of a block (see
`Valid Block Structures`_).

.. caution::
    Some blocks impose additional restrictions on how blocks may be nested within their
    parameters and payloads.
    One example is the ":term:`zero-depth`" restriction (used by some blocks, like the
    :class:`~ya_tagscript.blocks.IfBlock`).

    Check each block's documentation for additional restrictions beyond the basic
    structural ones.

Where possible, the inner nested blocks are interpreted only when necessary::

    {if(1>2):{command:echo reality is broken!!}|1 is still not larger than 2}

Obviously, the :class:`~ya_tagscript.blocks.CommandBlock` should only be interpreted
if the condition for the :class:`~ya_tagscript.blocks.IfBlock` is true (which isn't
the case here). Not all blocks are able to avoid side effects this precisely, so it is
a good idea to use an :class:`~ya_tagscript.blocks.IfBlock` with an easily checked
condition to determine whether to run a block with side effects that should only happen
under certain conditions.

.. literalinclude:: code_examples/nested_blocks_example.py
    :caption: You can go pretty wild with nesting blocks (this is still pretty tame)
    :language: Python
    :linenos:

.. note::
    The term "block" is used to refer to two slightly different things:

    - subclasses of :class:`~ya_tagscript.interfaces.BlockABC`: these are Python
      classes that the interpreter uses to process the string input to get the desired
      output
    - string structures like ``{declaration(parameter):payload}`` in scripts (which
      relate to a specific Python class that processes it, depending on the
      ``declaration``)

    A phrase such as "Use an :class:`~ya_tagscript.blocks.IfBlock` to make boolean
    checks" means to write a script that has a block like ``{if(1==1):success|failure}``.

    Context should make it obvious which one is being referred to. If you think
    additional clarification may be needed in a certain place, do not hesitate to open
    an issue on the `GitHub repository <https://github.com/MajorTanya/ya_tagscript>`_.

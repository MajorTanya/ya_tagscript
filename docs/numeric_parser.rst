=========================
The Numeric String Parser
=========================

For the particularly curious, here is the Numeric String Parser used by
:class:`~ya_tagscript.blocks.MathBlock`. There are some more functions, mainly internal
parsing helpers, that are not included here.

The Numeric String Parser is powered by
`PyParsing <https://pyparsing-docs.readthedocs.io/en/latest/>`_.

.. autoclass:: ya_tagscript.blocks.math.math_block.NumericStringParser
    :members: EPSILON, eval
    :no-show-inheritance:

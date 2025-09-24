========
Glossary
========

.. glossary::
    :sorted:

    work limit
        The interpreter's work limit is only an approximate limit. This is because a
        block can be short enough to not trigger the limiter while outputting more
        characters than its original body. Additionally, the work limit is referring to
        the maximum output size before processing is halted.

        **Example**:

        Imagine an interpreter with a work limit of 15 characters encountering the
        following script::

            {=(hello):Hello|Hi|Good day|Good morning|Good evening}
            {hello(4):|}
            {hello(5):|}
            {hello(1):|}

        This entire script is 90 characters long (not counting line breaks).
        The work limit is 15, so the output should not (massively) exceed 15
        characters.

        *Referenced by*:

        .. styled-list::
           :class: x-ref-col

           - :class:`~ya_tagscript.interfaces.InterpreterABC`
           - :class:`~ya_tagscript.interpreter.TagScriptInterpreter`

    zero-depth
        For certain inputs, the splitting delimiter must not be contained within a
        nested block, for example within a variable block that is being retrieved for
        splitting.

        **Correct Examples**:

        #. The :class:`~ya_tagscript.blocks.AnyBlock` requires ``|`` in ``parameter``
           and ``payload``::

                {any({my_var}==test|{other_var}):{msg}|{error_msg}}

           The :class:`~ya_tagscript.blocks.AnyBlock` requires ``|`` as separators of
           the conditions and to split the responses. The above example will succeed
           if ``{my_var}`` equals ``"test"`` OR if ``{other_var}`` contains a truthy
           expression.

           - On success, the ``{msg}`` block is interpreted and returned.
           - On failure, the ``{error_msg}`` block is interpreted and returned.

        #. The :class:`~ya_tagscript.blocks.ListBlock` requires tildes (``~``) in
           ``payload``::

                {list({index}):{first}~{second}~third~fourth}

           The :class:`~ya_tagscript.blocks.ListBlock` requires list items to be split
           by tildes (``~``). The above example will succeed and return the appropriate
           item, e.g. "third" if ``{index}`` is ``2`` (remember: the
           :class:`~ya_tagscript.blocks.ListBlock` is 0-indexed) or the interpreted
           result of ``{first}`` if ``{index}`` is ``0``.

        **Incorrect Examples**:

        #. :class:`~ya_tagscript.blocks.AnyBlock` with ``|`` not at zero-depth in
           ``parameter``::

                {any({conditions}):Success|Failure}

           This :class:`~ya_tagscript.blocks.AnyBlock` will ONLY work as expected if
           ``{conditions}`` is literally "true" or "false" (which are special-cased
           constants for boolean expressions).

           For all other situations, it will only return the ``Failure`` reply because
           ``{conditions}`` is not a proper boolean expression.

        #. :class:`~ya_tagscript.blocks.AnyBlock` with ``|`` not at zero-depth in
           ``payload``::

                {any({my_var}==test|{other_var}):{outcomes}}

           This :class:`~ya_tagscript.blocks.AnyBlock` has the same conditions as in
           the Correct Example above, **BUT**:

           - On success, the *entire* ``{outcomes}`` block is interpreted and returned
           - On failure, nothing is interpreted and an empty string is returned

           .. note::
            This MAY be desirable for situations where the failure case should
            return an empty string. However, it is worth making this intent clear
            by writing the block like this, with an empty string in the failure case
            section::

                {any({my_var}==test|{other_var}):{outcomes}|}

            (A better variable name to replace ``outcomes`` would also be worth
            considering.)

        #. :class:`~ya_tagscript.blocks.ListBlock` with ``~`` not at zero-depth in
           ``payload``::

                {list({index}):{list_of_things}}

           This :class:`~ya_tagscript.blocks.ListBlock` will always return the entire
           interpreted contents of ``{list_of_things}`` because there is no zero-depth
           ``~`` to split the list items.

        *Referenced by*:

        .. styled-list::
           :class: x-ref-col

           - Introduction to :ref:`Nesting Blocks`
           - :class:`~ya_tagscript.blocks.AllBlock`
           - :class:`~ya_tagscript.blocks.AnyBlock`
           - :class:`~ya_tagscript.blocks.DebugBlock`
           - :class:`~ya_tagscript.blocks.EmbedBlock` (since v1.5.0)
           - :class:`~ya_tagscript.blocks.IfBlock`
           - :class:`~ya_tagscript.blocks.CycleBlock` (does not have the requirement)
           - :class:`~ya_tagscript.blocks.ListBlock` (does not have the requirement)
           - :class:`~ya_tagscript.blocks.RandomBlock` (does not have the requirement)

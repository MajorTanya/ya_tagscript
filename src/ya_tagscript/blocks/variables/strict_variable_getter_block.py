from ...interfaces import BlockABC
from ...interpreter import Context


class StrictVariableGetterBlock(BlockABC):
    """
    This block attempts to fetch the value of a variable declared in the script. If the
    variable exists, its value is returned; otherwise, the block is rejected and not
    interpreted at all.

    Note:
        In contrast to the :class:`LooseVariableGetterBlock`, this block checks for the
        existence of the variable during the earlier
        :meth:`StrictVariableGetterBlock.will_accept` phase, rejecting the block early
        if the variable does not exist already.

    **Usage**: ``{<variable name>}``

    **Aliases**: N/A

    **Parameter**: ``None``

    **Payload**: ``None``

    **Examples**::

        # Variables can be assigned with the AssignmentBlock
        # or supplied to the interpreter via the seed_variables kwarg
        {assign(user_name):Carl}

        {user_name}
        # Carl

        {non_existent_variable}
        # This block is rejected because the variable doesn't exist (Output below line):
        # ---
        # {non_existent_variable}

    See Also:

        :ref:`partial-substring-retrieval`
            How to retrieve only parts of a string variable (part of the
            :class:`~ya_tagscript.adapters.StringAdapter` documentation).
    """

    @property
    def _accepted_names(self) -> None:
        return None

    def will_accept(self, ctx: Context) -> bool:
        """
        Checks whether the declaration, when interpreted, exists as a variable name.

        Parameters
        ----------
        ctx : Context
            The current Context to check for acceptability

        Returns
        -------
        bool
            Whether this block can process the provided Context
        """
        # override because this doesn't use declarations but checks variable existence
        if (declaration := ctx.node.declaration) is None:
            return False
        return ctx.interpret_segment(declaration) in ctx.response.variables

    def process(self, ctx: Context) -> str | None:
        if (declaration := ctx.node.declaration) is None:
            return None

        parsed_declaration = ctx.interpret_segment(declaration)
        if (adapter := ctx.response.variables.get(parsed_declaration)) is None:
            return None

        return adapter.get_value(ctx)

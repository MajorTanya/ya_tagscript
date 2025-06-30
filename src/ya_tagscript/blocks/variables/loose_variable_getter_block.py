from typing import Literal

from ...interfaces import BlockABC
from ...interpreter import Context


class LooseVariableGetterBlock(BlockABC):
    """
    This block attempts to fetch the value of a variable declared in the script. If the
    variable exists, its value is returned; otherwise, the block is rejected and not
    interpreted at all.

    Note:
        In contrast to the :class:`StrictVariableGetterBlock`, this block checks for
        the existence of the variable only during processing.
        The earlier call to :meth:`LooseVariableGetterBlock.will_accept` always returns
        :data:`True`.

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

    def will_accept(self, ctx: Context) -> Literal[True]:
        """
        Will always return :data:`True` since the block only checks for variable
        existence during processing.

        Parameters
        ----------
        ctx : Context
            The Context to check for acceptability (the block ignores this parameter)

        Returns
        -------
        :class:`Literal[True]`
            Always returns :data:`True` because preconditions are only checked during
            processing.
        """
        # override because this checks later during processing if the variable exists
        return True

    def process(self, ctx: Context) -> str | None:
        if (declaration := ctx.node.declaration) is None:
            return None

        parsed_declaration = ctx.interpret_segment(declaration)
        if (adapter := ctx.response.variables.get(parsed_declaration)) is None:
            return None

        return adapter.get_value(ctx)

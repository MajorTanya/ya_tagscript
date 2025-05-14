from ...adapters import StringAdapter
from ...interfaces import BlockABC
from ...interpreter import Context


class AssignmentBlock(BlockABC):
    """
    This block assigns a value to a variable within the context of the script.

    The payload represents the value to be assigned, while the parameter specifies
    the variable name. The variable can then be referenced elsewhere in the script.

    **Usage**: ``{assign(<variable name>):<value>}``

    **Aliases**: ``=``, ``assign``, ``let``, ``var``

    **Parameter**: ``variable name`` (required)

    **Payload**: ``value`` (required)

    **Examples**::

        {assign(prefix):!}
        The prefix here is `{prefix}`.
        # The prefix here is `!`.

        {assign(day):Monday}
        {if({day}==Wednesday):It's Wednesday my dudes!|The day is {day}.}
        # The day is Monday.
    """

    requires_any_parameter = True
    requires_any_payload = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"=", "assign", "let", "var"}

    def process(self, ctx: Context) -> str | None:
        if (param := ctx.node.parameter) is None:
            return None
        elif (payload := ctx.node.payload) is None:
            return None

        parsed_parameter = ctx.interpret_segment(param)
        parsed_payload = ctx.interpret_segment(payload)
        ctx.response.set_variable(parsed_parameter, StringAdapter(parsed_payload))
        return ""

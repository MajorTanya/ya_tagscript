from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import parse_condition, split_at_substring_zero_depth


class AllBlock(BlockABC):
    """
    This block checks that all provided expressions are true.

    Multiple boolean expressions in the parameter must be separated by ``|`` at
    ":term:`zero-depth`", meaning ``|`` cannot be added dynamically. See the examples
    for clarification.

    The payload includes the message the block should output.

    To provide outputs for both the success and failure cases, the payload must be
    split by ``|`` at ":term:`zero-depth`". The part before the ``|`` represents the
    success case, the part after represents the failure case.

    If no ``|`` can be found at ":term:`zero-depth`", the entire payload represents the
    success case, with no output being returned for the failure case.

    If the string for a given case is empty, no output is returned for it.

    **Usage**: ``{all(<expression|expression|...>):<message>}``

    **Aliases**: ``all``, ``and``

    **Parameter**: ``expression`` (required)

    **Payload**: ``message`` (required)

    **Examples**::

        # note how | is at "zero-depth" for the expressions and the responses
        {all({args}>=100|{args}<=1000):You picked {args}.|You must provide a number between 100 and 1000.}
        # if {args} is 52
        You must provide a number between 100 and 1000.

        # if {args} is 282
        You picked 282.

        {all(1==1|2==1):This is my success case message}
        # since these conditions fail and no failure case message is defined, no output
        # is produced

        {all(1==1|hi==hi):|This is my failure case message}
        # since the message is empty before the |, meaning no success case message is
        # defined, no output is produced

        # If the payload is fully nested, it is considered the success case message
        # Here, it is obviously _intended_ to be split by the IfBlock but that does not
        # happen due to the "zero-depth" separator requirement in payloads
        {=(msgs):Success msg|Failure msg}
        {all(true|1==1):{msgs}}
        # Success msg|Failure msg

    """

    requires_nonempty_parameter = True
    requires_nonempty_payload = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"all", "and"}

    def process(self, ctx: Context) -> str | None:
        if (parameter := ctx.node.parameter) is None or parameter.strip() == "":
            return None
        elif (payload := ctx.node.payload) is None or payload.strip() == "":
            return None

        conditions = split_at_substring_zero_depth(parameter, "|")
        check_results = [parse_condition(ctx, cond) for cond in conditions]

        if "|" not in payload:
            # zero-depth requirement means this is assumed a "success-only" payload
            split_out = [payload]
        else:
            split_out = split_at_substring_zero_depth(payload, "|", max_split=1)

        if len(split_out) == 1:
            positive_out = split_out[0]
            negative_out = None
        else:
            positive_out = split_out[0]
            negative_out = split_out[1]

        result = all(check_results)
        if result:
            return ctx.interpret_segment(positive_out)
        elif (not result) and (negative_out is not None):
            return ctx.interpret_segment(negative_out)
        else:
            return ""

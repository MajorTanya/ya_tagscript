from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import parse_condition, split_at_substring_zero_depth


class IfBlock(BlockABC):
    """
    This block checks whether the provided condition is true or not and then returns
    the appropriate message.

    The payload includes the message the block should output.

    To provide outputs for both the success and failure cases, the payload must be
    split by ``|`` at ":term:`zero-depth`". The part before the ``|`` represents the
    success case, the part after represents the failure case.

    If no ``|`` can be found at ":term:`zero-depth`", the entire payload represents the
    success case, with no output being returned for the failure case.

    If the string for a given case is empty, no output is returned for it.

    **Usage**: ``{if(<condition>):<message>}``

    **Aliases**: ``if``

    **Parameter**: ``condition`` (required)

    **Payload**: ``message`` (required)

    **Examples**::

        {if({args}==63):You guessed it! The number I was thinking of was 63!|Too {if({args}<63):low|high}, try again.}
        # if args is 63
        You guessed it! The number I was thinking of was 63!

        # if {args} is 73
        Too high, try again.

        # if {args} is 14
        Too low, try again.

        {if(false):This is my success case message}
        # since this condition fails and no failure case message is defined, no output
        # is produced

        {if(true):|This is my failure case message}
        # since the message is empty before the |, meaning no success case message is
        # defined, no output is produced

        # If the payload is fully nested, it is considered the success case message
        # Here, it is obviously _intended_ to be split by the IfBlock but that does not
        # happen due to the "zero-depth" separator requirement in payloads
        {=(msgs):Success msg|Failure msg}
        {if(true):{msgs}}
        # Success msg|Failure msg

    Supported condition operators:

    +------------+--------------------------+---------+---------------------------------------------+
    | Operator   | Check                    | Example | Description                                 |
    +============+==========================+=========+=============================================+
    | ``==``     | equality                 | a==a    | value 1 is equal to value 2                 |
    +------------+--------------------------+---------+---------------------------------------------+
    | ``!=``     | inequality               | a!=b    | value 1 is not equal to value 2             |
    +------------+--------------------------+---------+---------------------------------------------+
    | ``>``      | greater than             | 5>3     | value 1 is greater than value 2             |
    +------------+--------------------------+---------+---------------------------------------------+
    | ``<``      | less than                | 4<8     | value 1 is less than value 2                |
    +------------+--------------------------+---------+---------------------------------------------+
    | ``>=``     | greater than or equality | 10>=10  | value 1 is greater than or equal to value 2 |
    +------------+--------------------------+---------+---------------------------------------------+
    | ``<=``     | less than or equality    | 5<=6    | value 1 is less than or equal to value 2    |
    +------------+--------------------------+---------+---------------------------------------------+
    | ``true``   | constant true            | true    | always true                                 |
    +------------+--------------------------+---------+---------------------------------------------+
    | ``false``  | constant false           | false   | always false                                |
    +------------+--------------------------+---------+---------------------------------------------+
    """

    requires_nonempty_parameter = True
    requires_nonempty_payload = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"if"}

    def process(self, ctx: Context) -> str | None:
        if (parameter := ctx.node.parameter) is None or parameter.strip() == "":
            return None
        elif (payload := ctx.node.payload) is None or payload.strip() == "":
            return None

        if (condition_fulfilled := parse_condition(ctx, parameter)) is None:
            return ""

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

        if condition_fulfilled:
            return ctx.interpret_segment(positive_out)
        elif (not condition_fulfilled) and (negative_out is not None):
            return ctx.interpret_segment(negative_out)
        else:
            return ""

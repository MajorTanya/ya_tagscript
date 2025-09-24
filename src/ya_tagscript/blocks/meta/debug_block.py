"""
Debug Block adapted from benz206's bTagScript, licensed under Creative Commons
Attribution 4.0 International License (CC BY 4.0).

cf. https://github.com/benz206/bTagScript/blob/945b8e34750debea714d36de863412e189975c1b/bTagScript/block/util_blocks/debug_block.py
"""

from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import split_at_substring_zero_depth


class DebugBlock(BlockABC):
    """
    This block will output a dictionary of all variables known at the time of
    processing under the ``debug`` key of the
    :attr:`~ya_tagscript.interpreter.Response.extra_kwargs` attribute of the
    :class:`~ya_tagscript.interpreter.Response` object.

    Separate the variables you want to include or exclude with a comma (``,``) or
    a tilde (``~``). These separations must be consistent (only commas or only tildes)
    and be located at ":term:`zero-depth`", i.e. only separators present before
    interpretation will be used for splitting..

    If no parameter and no payload are provided, all variables will be included.
    (``{debug}``, which is equivalent to ``{debug(exclude):}``)

    If no parameter is provided but a payload exists, only variables included in the
    payload will be included.
    (``{debug:my_var}``, which is equivalent to: ``{debug(include):my_var}``)

    Note:
        This should always be placed at the very bottom, it will not include any
        variables (re-)defined after its location in the script.

    **Usage**: ``{debug(["i"|"include"|"e"|"exclude"]):<variables>}``

    **Aliases**: ``debug``

    **Parameter**: one of ``i``, ``include``, ``e``, ``exclude``

    **Payload**: ``variables``

    **Examples**::

        # In the following example, the desired output is "Hello" but instead "Bye" is
        returned:

        {=(something):Hello/World}
        {=(parsed):{something(1)}}
        {if({parsed}==Hello):Hello|Bye}
        # Bye

        # We can investigate by adding the DebugBlock at the end of the script:

        {debug}

        # This will return a dictionary with all known variable names and their values
        # at the time of this block's processing.

        # In this example, the dictionary would look like this (Python)
        {
            "something": "Hello/World",
            "parsed": "Hello/World",
        }

        # Now we can see that the definition of parsed is missing a custom delimiter in
        # order to split the value on the slash /
        # We can fix this:

        {=(something):Hello/World}
        {=(parsed):{something(1):/}}
        {if({parsed}==Hello):Hello|Bye}
        # Hello

        ####

        # Note how the variables names are split by zero-depth commas and not in a nested block:
        # (assume these exist)
        {debug:my_var,another var}

    **Response Attribute**:

    This block sets the following attribute on the
    :class:`~ya_tagscript.interpreter.Response` object:

    - :attr:`~ya_tagscript.interpreter.Response.extra_kwargs`
        - ``extra_kwargs["debug"]``: :class:`dict[str, str]` — A dictionary with all
          known variables at the time of interpretation (variable names are mapped to
          their values)

    Note:
        This block only sets the ``debug``
        :attr:`~ya_tagscript.interpreter.Response.extra_kwargs` key as shown above. It
        is the *responsibility of the client* to somehow surface this data to the user,
        if this is desired.
    """

    @property
    def _accepted_names(self) -> set[str]:
        return {"debug"}

    def process(self, ctx: Context) -> str | None:
        debug: dict[str, str | None] = {}
        requested_variables: list[str] = []

        if (param := ctx.node.parameter) is not None:
            param = ctx.interpret_segment(param)

        if (payload := ctx.node.payload) is not None:
            split_payload = split_at_substring_zero_depth(payload, "~")
            if len(split_payload) == 1 and split_payload[0] == payload:
                split_payload = split_at_substring_zero_depth(payload, ",")
            for req_v in split_payload:
                requested_variables.append(ctx.interpret_segment(req_v))

        exclude_requested = param in ("e", "exc", "exclude")
        include_requested = param in ("i", "inc", "include")

        if exclude_requested or include_requested:
            if payload is None:
                return None
            # user has specified in-/exclusion, filter accordingly
            for k, v in ctx.response.variables.items():
                if (exclude_requested and k not in requested_variables) or (
                    include_requested and k in requested_variables
                ):
                    debug[k] = v.get_value(ctx)
        elif payload is not None:
            # no parameter specified, treat as "include", filter accordingly
            for k, v in ctx.response.variables.items():
                if k in requested_variables:
                    debug[k] = v.get_value(ctx)
        else:
            # no parameter and no payload, user requested everything
            for k, v in ctx.response.variables.items():
                debug[k] = v.get_value(ctx)

        ctx.response.extra_kwargs["debug"] = debug
        return ""

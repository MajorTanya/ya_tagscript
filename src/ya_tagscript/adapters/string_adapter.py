from ..interfaces import AdapterABC
from ..interpreter import Context
from ..util import escape_content


class StringAdapter(AdapterABC):
    """An adapter for strings

    .. _partial-substring-retrieval:

    Retrieving partial substrings with parameters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    You can optionally use parameters to limit what parts of the string should be
    retrieved.

    If you provide a single number n as the parameter, the n-th word of the string is
    returned (split by spaces). The first word is at index 1, and so on (1-indexed).

    **Examples**::

        # Assume my_string_variable holds "Hello there. General Kenobi."
        {my_string_variable(2)}
        # there.

        {my_string_variable(3)}
        # General

    If you provide a single number followed (or preceded) by a plus, all words after
    (or before) are returned (split by spaces).

    **Examples**::

        # Assume my_string_variable holds "Hello there. General Kenobi."
        {my_string_variable(3+)}
        # General Kenobi.

        {my_string_variable(+2)}
        # Hello there.

    You can define the characters to split the string on by passing a payload. The
    string will then be split at occurrences of those characters.

    **Examples**::

        # Assume my_string_variable holds "Hello there. General Kenobi."
        {my_string_variable(2):.}
        # General Kenobi

        {my_string_variable(3):en}
        # obi.
    """

    def __init__(self, string: str, *, should_escape: bool = False) -> None:
        self.string: str = str(string)
        self.should_escape: bool = should_escape

    def __repr__(self) -> str:
        return f"<{type(self).__qualname__} string={self.string!r}>"

    def get_value(self, ctx: Context) -> str | None:
        return self._return_value(self._handle_ctx(ctx))

    def _handle_ctx(self, ctx: Context) -> str:
        if (param := ctx.node.parameter) is None:
            return self.string

        parsed_param = ctx.interpret_segment(param)
        parsed_payload = (
            ctx.interpret_segment(ctx.node.payload)
            if ctx.node.payload is not None
            else None
        )

        try:
            if "+" not in parsed_param:
                index = int(parsed_param) - 1
                splitter = " " if parsed_payload is None else parsed_payload
                return self.string.split(splitter)[index]
            else:
                index = int(parsed_param.replace("+", "")) - 1
                splitter = " " if parsed_payload is None else parsed_payload
                if parsed_param.startswith("+"):
                    return splitter.join(self.string.split(splitter)[: index + 1])
                elif parsed_param.endswith("+"):
                    return splitter.join(self.string.split(splitter)[index:])
                else:
                    return self.string.split(splitter)[index]
        except (ValueError, IndexError):
            return self.string

    def _return_value(self, string: str) -> str | None:
        return escape_content(string) if self.should_escape else string

import logging
from typing import assert_never

from ya_tagscript.interfaces import NodeABC

from .node import Node
from .parse_state import BlockParseState, ParseState

# this is named "ts_parser" to avoid false positives against the (removed) "parser"
# module in the standard library

_log = logging.getLogger(__name__)


# fmt: off
BACKSLASH   = "\\"  # noqa: E221
BRACE_OPEN  = "{"  # noqa: E221
BRACE_CLOSE = "}"
PAREN_OPEN  = "("  # noqa: E221
PAREN_CLOSE = ")"
COLON       = ":"  # noqa: E221
# fmt: on


_SPECIAL_TOKENS: set[str] = {
    BRACE_OPEN,
    BRACE_CLOSE,
    PAREN_OPEN,
    PAREN_CLOSE,
    COLON,
}
# COLON isn't special in several places
_SPECIAL_TOKENS_NO_COLON = _SPECIAL_TOKENS - {COLON}


class TagScriptParser:

    __slots__ = ()

    def parse(self, input_str: str) -> list[NodeABC]:
        """Converts a string into a list of Nodes and handling nested blocks as text"""
        _nodes: list[NodeABC] = []
        _state = None
        _text_buffer = ""
        i = 0
        input_len = len(input_str)
        special_chars = _SPECIAL_TOKENS
        specials_no_colon = _SPECIAL_TOKENS_NO_COLON

        # region processing loop
        # this is an extremely hot loop so there are additional local references to
        # instance attributes in order to squeeze a bit more performance from the
        # parser
        char = ""
        while i < input_len:
            previous_char = char
            is_escaped = previous_char == BACKSLASH
            char = input_str[i]
            block: BlockParseState | None = _state
            current_state = block.state if block is not None else None

            if block is None and char not in special_chars:
                # fast path for of 0-level text chars
                start = i
                while i < input_len and input_str[i] not in special_chars:
                    i += 1
                _text_buffer += input_str[start:i]
                char = input_str[i - 1]
                continue

            # mainly a typing crutch since current_state = block.state (top of loop)
            if block is None or current_state is None:
                if char == BRACE_OPEN:
                    if is_escaped:
                        _text_buffer += char
                    else:
                        if len(_text_buffer) > 0:
                            _nodes.append(Node.text(text_value=_text_buffer))
                            _text_buffer = ""
                        _state = BlockParseState(
                            state=ParseState.EXPECTING_DECLARATION,
                            block_depth=1,
                        )
                else:
                    _text_buffer += char

            elif current_state is ParseState.EXPECTING_DECLARATION:
                # EXPECTING_DECLARATION is special:
                # - previous_char _must_ have been "{" at 0-depth for block start
                #   - is_escaped is always False
                #   - block depth == 1, paren_depth == 0 guaranteed
                # this is purely an assertion of this impossibility and thus not
                # covered (or coverable!) by tests
                if (
                    is_escaped or block.block_depth != 1 or block.paren_depth != 0
                ):  # pragma: no cover
                    raise AssertionError(
                        (
                            f"Invalid state in parser! EXPECTING_DECLARATION got: "
                            f"{is_escaped=}, {block.block_depth=}, "
                            f"{block.paren_depth=}"
                        ),
                    )
                if char == BRACE_OPEN:
                    # escaping is impossible in this state, must be nested block
                    block.block_depth += 1
                    block.transition_state(ParseState.IN_DECLARATION)
                    block.declaration = char
                elif char == BRACE_CLOSE:
                    # state guarantees: previous_char is "{" and block_depth == 1
                    _text_buffer += "{}"
                    _state = None
                elif char == PAREN_OPEN:
                    block.paren_depth += 1
                    block.transition_state(ParseState.IN_DECLARATION)
                    block.declaration = char
                elif char == PAREN_CLOSE:
                    block.transition_state(ParseState.IN_DECLARATION)
                    block.declaration = char
                    # state guarantee: paren_depth == 0, so can't decrement depth
                else:
                    # covers BACKSLASH, COLON, any other char
                    block.transition_state(ParseState.IN_DECLARATION)
                    block.declaration = char

            elif current_state is ParseState.IN_DECLARATION:
                if char not in special_chars:
                    # covers BACKSLASH and any other char
                    # fast-path accumulation
                    start = i
                    while i < input_len and input_str[i] not in special_chars:
                        i += 1
                    block.declaration = (block.declaration or "") + input_str[start:i]
                    char = input_str[i - 1]
                    continue
                elif char == BRACE_OPEN:
                    if not is_escaped:
                        block.block_depth += 1
                    block.declaration = (block.declaration or "") + char
                elif char == BRACE_CLOSE:
                    if block.block_depth == 1:
                        if is_escaped:
                            block.declaration = (block.declaration or "") + char
                        else:
                            _nodes.append(block.finalize())
                            _state = None
                    else:
                        if not is_escaped:
                            block.block_depth -= 1
                        block.declaration = (block.declaration or "") + char
                elif char == PAREN_OPEN:
                    block.paren_depth += 1
                    if block.block_depth == 1:
                        block.has_parameter_section = True
                        block.transition_state(ParseState.IN_PARAMETER)
                    else:
                        block.declaration = (block.declaration or "") + char
                elif char == PAREN_CLOSE:
                    block.declaration = (block.declaration or "") + char
                    if block.paren_depth > 0:
                        block.paren_depth -= 1
                elif char == COLON:
                    if block.block_depth == 1:
                        block.has_payload_section = True
                        block.transition_state(ParseState.IN_PAYLOAD)
                    else:
                        block.declaration = (block.declaration or "") + char
                else:
                    raise ValueError(f"Unknown special char {char!r} in IN_DECLARATION")

            elif current_state is ParseState.IN_PARAMETER:
                if char not in specials_no_colon:
                    # covers BACKSLASH, COLON, any other char
                    # fast-path accumulation
                    start = i
                    while i < input_len and input_str[i] not in specials_no_colon:
                        i += 1
                    block.parameter = (block.parameter or "") + input_str[start:i]
                    char = input_str[i - 1]
                    continue
                elif char == BRACE_OPEN:
                    if not is_escaped:
                        block.block_depth += 1
                    block.parameter = (block.parameter or "") + char
                elif char == BRACE_CLOSE:
                    if block.block_depth == 1:
                        if is_escaped:
                            block.parameter = (block.parameter or "") + char
                        else:
                            # invalid block, abandon
                            _text_buffer += _reconstruct_partial_block(block) + char
                            _state = None
                    else:
                        if not is_escaped:
                            block.block_depth -= 1
                        block.parameter = (block.parameter or "") + char
                elif char == PAREN_OPEN:
                    block.paren_depth += 1
                    block.parameter = (block.parameter or "") + char
                elif char == PAREN_CLOSE:
                    if block.paren_depth == 1:
                        block.transition_state(ParseState.POST_PARAMETER)
                    else:
                        block.parameter = (block.parameter or "") + char
                    block.paren_depth -= 1
                else:
                    raise ValueError(f"Unknown special char {char!r} in IN_PARAMETER")

            elif current_state is ParseState.POST_PARAMETER:
                if char == BRACE_CLOSE and block.block_depth == 1:
                    _nodes.append(block.finalize())
                    _state = None
                elif char == COLON and block.block_depth == 1:
                    block.has_payload_section = True
                    block.transition_state(ParseState.IN_PAYLOAD)
                else:
                    # by state guarantee
                    # covers BRACE_OPEN, BRACE_CLOSE (higher depth), PAREN_OPEN,
                    # PAREN_CLOSE, COLON (higher depth), BACKSLASH, any other char
                    # only colon or pop is allowed here, abort the block entirely
                    _text_buffer += _reconstruct_partial_block(block) + char
                    _state = None

            elif current_state is ParseState.IN_PAYLOAD:
                if char not in specials_no_colon:
                    # covers BACKSLASH, COLON, any other char
                    # fast-path accumulation
                    start = i
                    while i < input_len and input_str[i] not in specials_no_colon:
                        i += 1
                    block.payload = (block.payload or "") + input_str[start:i]
                    char = input_str[i - 1]
                    continue
                elif char == BRACE_OPEN:
                    if not is_escaped:
                        block.block_depth += 1
                    block.payload = (block.payload or "") + char
                elif char == BRACE_CLOSE:
                    if block.block_depth == 1:
                        if is_escaped:
                            block.payload = (block.payload or "") + char
                        else:
                            _nodes.append(block.finalize())
                            _state = None
                    else:
                        if not is_escaped:
                            block.block_depth -= 1
                        block.payload = (block.payload or "") + char
                elif char == PAREN_OPEN:
                    block.paren_depth += 1
                    block.payload = (block.payload or "") + char
                elif char == PAREN_CLOSE:
                    block.payload = (block.payload or "") + char
                    if block.paren_depth > 0:
                        block.paren_depth -= 1
                else:
                    raise ValueError(f"Unknown special char {char!r} in IN_PAYLOAD")

            else:
                assert_never(current_state)

            i += 1
        # endregion end of processing loop

        # Handle any remaining text or unclosed blocks
        if len(_text_buffer) > 0:
            _nodes.append(Node.text(text_value=_text_buffer))
            _text_buffer = ""
        block = _state
        if block is not None:
            # partial block state means at least a BRACE_OPEN, meaning there will always
            # be _some_ partial block to output as a TEXT Node
            _nodes.append(Node.text(text_value=_reconstruct_partial_block(block)))
            _state = None

        return _nodes


def _reconstruct_partial_block(block: BlockParseState) -> str:
    """Reconstructs a partial block as text for error recovery."""
    out = BRACE_OPEN
    if block.declaration is not None:
        out += block.declaration
    if block.has_parameter_section:
        out += PAREN_OPEN
        if block.parameter is not None:
            out += block.parameter
        if block.state is not ParseState.IN_PARAMETER:
            out += PAREN_CLOSE
        # otherwise this is a block being abandoned mid-parameter, so no closing paren
    if block.has_payload_section:
        out += COLON
        if block.payload is not None:
            out += block.payload
    return out

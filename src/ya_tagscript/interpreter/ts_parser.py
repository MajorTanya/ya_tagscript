import logging
from typing import assert_never

from ya_tagscript.interfaces import NodeABC

from .node import Node
from .parse_state import ParseState, transition_state

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


def parse_tagscript(input_str: str) -> list[NodeABC]:
    """Converts a string into a list of Nodes and handling nested blocks as text"""
    _nodes: list[NodeABC] = []
    _text_buffer = ""
    i = 0
    input_len = len(input_str)
    special_chars = _SPECIAL_TOKENS
    specials_no_colon = _SPECIAL_TOKENS_NO_COLON

    # initial block data
    block_state = None
    declaration = None
    parameter = None
    payload = None
    found_param_section = False
    found_payload_section = False
    block_depth = 0
    paren_depth = 0

    # region processing loop
    # this is an extremely hot loop so there are additional local references to
    # instance attributes in order to squeeze a bit more performance from the
    # parser
    char = ""
    while i < input_len:
        previous_char = char
        is_escaped = previous_char == BACKSLASH
        char = input_str[i]

        if block_state is None and char not in special_chars:
            # fast path for of 0-level text chars
            start = i
            while i < input_len and input_str[i] not in special_chars:
                i += 1
            _text_buffer += input_str[start:i]
            char = input_str[i - 1]
            continue

        if block_state is None:
            if char == BRACE_OPEN:
                if is_escaped:
                    _text_buffer += char
                else:
                    if len(_text_buffer) > 0:
                        _nodes.append(Node.text(text_value=_text_buffer))
                        _text_buffer = ""
                    block_state = ParseState.EXPECTING_DECLARATION
                    block_depth = 1
                    # reset block data
                    declaration = None
                    parameter = None
                    payload = None
                    found_param_section = False
                    found_payload_section = False
                    paren_depth = 0
            else:
                _text_buffer += char

        elif block_state is ParseState.EXPECTING_DECLARATION:
            # EXPECTING_DECLARATION is special:
            # - previous_char _must_ have been "{" at 0-depth for block start
            #   - is_escaped is always False
            #   - block depth == 1, paren_depth == 0 guaranteed
            # this is purely an assertion of this impossibility and thus not
            # covered (or coverable!) by tests
            if is_escaped or block_depth != 1 or paren_depth != 0:  # pragma: no cover
                raise AssertionError(
                    (
                        f"Invalid state in parser! EXPECTING_DECLARATION got: "
                        f"{is_escaped=}, {block_depth=}, "
                        f"{paren_depth=}"
                    ),
                )
            if char == BRACE_OPEN:
                # escaping is impossible in this state, must be nested block
                block_depth += 1
                block_state = transition_state(block_state, ParseState.IN_DECLARATION)
                declaration = char
            elif char == BRACE_CLOSE:
                # state guarantees: previous_char is "{" and block_depth == 1
                _text_buffer += "{}"
                block_state = None
            elif char == PAREN_OPEN:
                paren_depth += 1
                block_state = transition_state(block_state, ParseState.IN_DECLARATION)
                declaration = char
            elif char == PAREN_CLOSE:
                block_state = transition_state(block_state, ParseState.IN_DECLARATION)
                declaration = char
                # state guarantee: paren_depth == 0, so can't decrement depth
            else:
                # covers BACKSLASH, COLON, any other char
                block_state = transition_state(block_state, ParseState.IN_DECLARATION)
                declaration = char

        elif block_state is ParseState.IN_DECLARATION:
            if char not in special_chars:
                # covers BACKSLASH and any other char
                # fast-path accumulation
                start = i
                while i < input_len and input_str[i] not in special_chars:
                    i += 1
                declaration = (declaration or "") + input_str[start:i]
                char = input_str[i - 1]
                continue
            elif char == BRACE_OPEN:
                if not is_escaped:
                    block_depth += 1
                declaration = (declaration or "") + char
            elif char == BRACE_CLOSE:
                if block_depth == 1:
                    if is_escaped:
                        declaration = (declaration or "") + char
                    else:
                        if declaration is None:  # pragma: no cover
                            # we have at least one character to be in this state
                            raise AssertionError(
                                "Declaration cannot be None within IN_DECLARATION",
                            )
                        _nodes.append(
                            create_block_node(
                                declaration,
                                parameter,
                                found_param_section,
                                payload,
                                found_payload_section,
                            ),
                        )
                        block_state = None
                else:
                    if not is_escaped:
                        block_depth -= 1
                    declaration = (declaration or "") + char
            elif char == PAREN_OPEN:
                paren_depth += 1
                if block_depth == 1:
                    found_param_section = True
                    block_state = transition_state(block_state, ParseState.IN_PARAMETER)
                else:
                    declaration = (declaration or "") + char
            elif char == PAREN_CLOSE:
                declaration = (declaration or "") + char
                if paren_depth > 0:
                    paren_depth -= 1
            elif char == COLON:
                if block_depth == 1:
                    found_payload_section = True
                    block_state = transition_state(block_state, ParseState.IN_PAYLOAD)
                else:
                    declaration = (declaration or "") + char
            else:
                raise ValueError(f"Unknown special char {char!r} in IN_DECLARATION")

        elif block_state is ParseState.IN_PARAMETER:
            if char not in specials_no_colon:
                # covers BACKSLASH, COLON, any other char
                # fast-path accumulation
                start = i
                while i < input_len and input_str[i] not in specials_no_colon:
                    i += 1
                parameter = (parameter or "") + input_str[start:i]
                char = input_str[i - 1]
                continue
            elif char == BRACE_OPEN:
                if not is_escaped:
                    block_depth += 1
                parameter = (parameter or "") + char
            elif char == BRACE_CLOSE:
                if block_depth == 1:
                    if is_escaped:
                        parameter = (parameter or "") + char
                    else:
                        # invalid block, abandon
                        _text_buffer += (
                            _reconstruct_partial_block(
                                block_state,
                                declaration,
                                found_param_section,
                                parameter,
                                found_payload_section,
                                payload,
                            )
                            + char
                        )
                        block_state = None
                else:
                    if not is_escaped:
                        block_depth -= 1
                    parameter = (parameter or "") + char
            elif char == PAREN_OPEN:
                paren_depth += 1
                parameter = (parameter or "") + char
            elif char == PAREN_CLOSE:
                if paren_depth == 1:
                    block_state = transition_state(
                        block_state,
                        ParseState.POST_PARAMETER,
                    )
                else:
                    parameter = (parameter or "") + char
                paren_depth -= 1
            else:
                raise ValueError(f"Unknown special char {char!r} in IN_PARAMETER")

        elif block_state is ParseState.POST_PARAMETER:
            if char == BRACE_CLOSE and block_depth == 1:
                if declaration is None:  # pragma: no cover
                    # we must have gone through IN_DECLARATION so this cannot happen
                    raise AssertionError("Declaration cannot be None in POST_PARAMETER")
                _nodes.append(
                    create_block_node(
                        declaration,
                        parameter,
                        found_param_section,
                        payload,
                        found_payload_section,
                    ),
                )
                block_state = None
            elif char == COLON and block_depth == 1:
                found_payload_section = True
                block_state = transition_state(block_state, ParseState.IN_PAYLOAD)
            else:
                # by state guarantee
                # covers BRACE_OPEN, BRACE_CLOSE (higher depth), PAREN_OPEN,
                # PAREN_CLOSE, COLON (higher depth), BACKSLASH, any other char
                # only colon or pop is allowed here, abort the block entirely
                _text_buffer += (
                    _reconstruct_partial_block(
                        block_state,
                        declaration,
                        found_param_section,
                        parameter,
                        found_payload_section,
                        payload,
                    )
                    + char
                )
                block_state = None

        elif block_state is ParseState.IN_PAYLOAD:
            if char not in specials_no_colon:
                # covers BACKSLASH, COLON, any other char
                # fast-path accumulation
                start = i
                while i < input_len and input_str[i] not in specials_no_colon:
                    i += 1
                payload = (payload or "") + input_str[start:i]
                char = input_str[i - 1]
                continue
            elif char == BRACE_OPEN:
                if not is_escaped:
                    block_depth += 1
                payload = (payload or "") + char
            elif char == BRACE_CLOSE:
                if block_depth == 1:
                    if is_escaped:
                        payload = (payload or "") + char
                    else:
                        if declaration is None:  # pragma: no cover
                            # we must have gone through IN_DECLARATION so this cannot happen
                            raise AssertionError(
                                "Declaration cannot be None in IN_PAYLOAD",
                            )
                        _nodes.append(
                            create_block_node(
                                declaration,
                                parameter,
                                found_param_section,
                                payload,
                                found_payload_section,
                            ),
                        )
                        block_state = None
                else:
                    if not is_escaped:
                        block_depth -= 1
                    payload = (payload or "") + char
            elif char == PAREN_OPEN:
                paren_depth += 1
                payload = (payload or "") + char
            elif char == PAREN_CLOSE:
                payload = (payload or "") + char
                if paren_depth > 0:
                    paren_depth -= 1
            else:
                raise ValueError(f"Unknown special char {char!r} in IN_PAYLOAD")

        else:
            assert_never(block_state)

        i += 1
    # endregion end of processing loop

    # Handle any remaining text or unclosed blocks
    if len(_text_buffer) > 0:
        _nodes.append(Node.text(text_value=_text_buffer))
    if block_state is not None:
        # partial block state means at least a BRACE_OPEN, meaning there will always
        # be _some_ partial block to output as a TEXT Node
        _nodes.append(
            Node.text(
                text_value=_reconstruct_partial_block(
                    block_state,
                    declaration,
                    found_param_section,
                    parameter,
                    found_payload_section,
                    payload,
                ),
            ),
        )

    return _nodes


def _reconstruct_partial_block(
    state: ParseState,
    declaration: str | None,
    has_parameter_section: bool,
    parameter: str | None,
    has_payload_section: bool,
    payload: str | None,
) -> str:
    """Reconstructs a partial block as text for error recovery."""
    out = BRACE_OPEN
    if declaration is not None:
        out += declaration
    if has_parameter_section:
        out += PAREN_OPEN
        if parameter is not None:
            out += parameter
        if state is not ParseState.IN_PARAMETER:
            out += PAREN_CLOSE
        # otherwise this is a block being abandoned mid-parameter, so no closing paren
    if has_payload_section:
        out += COLON
        if payload is not None:
            out += payload
    return out


def create_block_node(
    declaration: str,
    parameter: str | None,
    has_parameter_section: bool,
    payload: str | None,
    has_payload_section: bool,
) -> NodeABC:
    """Convert the parse state into a BLOCK type Node"""
    end_param = parameter if parameter is not None else None
    if has_parameter_section and end_param is None:
        end_param = ""

    end_payload = payload if payload is not None else None
    if has_payload_section and end_payload is None:
        end_payload = ""

    node = Node.block(
        declaration=declaration,
        parameter=end_param,
        payload=end_payload,
    )
    return node

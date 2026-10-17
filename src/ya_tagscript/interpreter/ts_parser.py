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
    block_state: ParseState | None = None
    declaration: str = ""
    parameter: str = ""
    payload: str = ""
    found_param_section: bool = False
    found_payload_section: bool = False
    block_depth: int = 0
    paren_depth: int = 0

    # region processing loop
    # this is an extremely hot loop
    while i < input_len:
        char = input_str[i]

        if block_state is None and char not in special_chars:
            # fast path for of 0-level text chars
            start = i
            while i < input_len and input_str[i] not in special_chars:
                i += 1
            _text_buffer += input_str[start:i]
            continue

        if block_state is None:
            if char == BRACE_OPEN:
                is_escaped = i > 0 and input_str[i - 1] == BACKSLASH
                if is_escaped:
                    _text_buffer += char
                else:
                    if len(_text_buffer) > 0:
                        _nodes.append(Node.text(text_value=_text_buffer))
                        _text_buffer = ""
                    block_state = ParseState.EXPECTING_DECLARATION
                    block_depth = 1
                    # reset block data
                    declaration = ""
                    parameter = ""
                    payload = ""
                    found_param_section = False
                    found_payload_section = False
                    paren_depth = 0
            else:
                _text_buffer += char

        elif block_state is ParseState.EXPECTING_DECLARATION:
            # EXPECTING_DECLARATION is special:
            # - previous_char _must_ have been "{" at 0-depth for block start
            #   - block depth == 1, paren_depth == 0 guaranteed
            # this is purely an assertion of this impossibility and thus not
            # covered (or coverable!) by tests
            if block_depth != 1 or paren_depth != 0:  # pragma: no cover
                raise AssertionError(
                    (
                        f"Invalid state in parser! EXPECTING_DECLARATION got: "
                        f"{block_depth=}, {paren_depth=}"
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
                declaration += input_str[start:i]
                continue
            elif char == BRACE_OPEN:
                is_escaped = i > 0 and input_str[i - 1] == BACKSLASH
                if not is_escaped:
                    block_depth += 1
                declaration += char
            elif char == BRACE_CLOSE:
                is_escaped = i > 0 and input_str[i - 1] == BACKSLASH
                if block_depth == 1:
                    if is_escaped:
                        declaration += char
                    else:
                        _nodes.append(
                            Node.block(
                                declaration=declaration,
                                parameter=parameter if found_param_section else None,
                                payload=payload if found_payload_section else None,
                            ),
                        )
                        block_state = None
                else:
                    if not is_escaped:
                        block_depth -= 1
                    declaration += char
            elif char == PAREN_OPEN:
                paren_depth += 1
                if block_depth == 1:
                    found_param_section = True
                    block_state = transition_state(block_state, ParseState.IN_PARAMETER)
                else:
                    declaration += char
            elif char == PAREN_CLOSE:
                declaration += char
                if paren_depth > 0:
                    paren_depth -= 1
            elif char == COLON:
                if block_depth == 1:
                    found_payload_section = True
                    block_state = transition_state(block_state, ParseState.IN_PAYLOAD)
                else:
                    declaration += char
            else:
                raise ValueError(f"Unknown special char {char!r} in IN_DECLARATION")

        elif block_state is ParseState.IN_PARAMETER:
            if char not in specials_no_colon:
                # covers BACKSLASH, COLON, any other char
                # fast-path accumulation
                start = i
                while i < input_len and input_str[i] not in specials_no_colon:
                    i += 1
                parameter += input_str[start:i]
                continue
            elif char == BRACE_OPEN:
                is_escaped = i > 0 and input_str[i - 1] == BACKSLASH
                if not is_escaped:
                    block_depth += 1
                parameter += char
            elif char == BRACE_CLOSE:
                is_escaped = i > 0 and input_str[i - 1] == BACKSLASH
                if block_depth == 1:
                    if is_escaped:
                        parameter += char
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
                    parameter += char
            elif char == PAREN_OPEN:
                paren_depth += 1
                parameter += char
            elif char == PAREN_CLOSE:
                if paren_depth == 1:
                    block_state = transition_state(
                        block_state,
                        ParseState.POST_PARAMETER,
                    )
                else:
                    parameter += char
                paren_depth -= 1
            else:
                raise ValueError(f"Unknown special char {char!r} in IN_PARAMETER")

        elif block_state is ParseState.POST_PARAMETER:
            if char == BRACE_CLOSE and block_depth == 1:
                _nodes.append(
                    Node.block(
                        declaration=declaration,
                        parameter=parameter if found_param_section else None,
                        payload=payload if found_payload_section else None,
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
                payload += input_str[start:i]
                continue
            elif char == BRACE_OPEN:
                is_escaped = i > 0 and input_str[i - 1] == BACKSLASH
                if not is_escaped:
                    block_depth += 1
                payload += char
            elif char == BRACE_CLOSE:
                is_escaped = i > 0 and input_str[i - 1] == BACKSLASH
                if block_depth == 1:
                    if is_escaped:
                        payload += char
                    else:
                        _nodes.append(
                            Node.block(
                                declaration=declaration,
                                parameter=parameter if found_param_section else None,
                                payload=payload if found_payload_section else None,
                            ),
                        )
                        block_state = None
                else:
                    if not is_escaped:
                        block_depth -= 1
                    payload += char
            elif char == PAREN_OPEN:
                paren_depth += 1
                payload += char
            elif char == PAREN_CLOSE:
                payload += char
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
    declaration: str,
    has_parameter_section: bool,
    parameter: str,
    has_payload_section: bool,
    payload: str,
) -> str:
    """Reconstructs a partial block as text for error recovery."""
    out = BRACE_OPEN + declaration
    if has_parameter_section:
        out += PAREN_OPEN + parameter
        if state is not ParseState.IN_PARAMETER:
            out += PAREN_CLOSE
        # otherwise this is a block being abandoned mid-parameter, so no closing paren
    if has_payload_section:
        out += COLON + payload
    return out

import logging
import re
from typing import assert_never

from ya_tagscript.interfaces import NodeABC

from .node import Node
from .parse_state import ParseState, transition_state

# this is named "ts_parser" to avoid false positives against the (removed) "parser"
# module in the standard library

_log = logging.getLogger(__name__)

_special_tokens_pattern = re.compile(r"[{}():]")
_special_tokens_no_colon_pattern = re.compile(r"[{}()]")
_braces_only_pattern = re.compile(r"[{}]")

# fmt: off
BACKSLASH   = "\\"  # noqa: E221
BRACE_OPEN  = "{"  # noqa: E221
BRACE_CLOSE = "}"
PAREN_OPEN  = "("  # noqa: E221
PAREN_CLOSE = ")"
COLON       = ":"  # noqa: E221
# fmt: on


def parse_tagscript(input_str: str) -> list[NodeABC]:
    """Converts a string into a list of Nodes and handling nested blocks as text"""
    _nodes: list[NodeABC] = []
    _text_buffer = ""
    i = 0
    input_len = len(input_str)

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

        if block_state is None:
            if char != BRACE_OPEN:
                # fast path for of 0-level text chars
                start = i
                i = input_str.find(BRACE_OPEN, start)
                if i == -1:
                    i = input_len
                _text_buffer += input_str[start:i]
                continue
            else:  # char == BRACE_OPEN
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
            declaration_i = i
            # inner loop until one of these things occurs:
            # - block closes with '}'
            # - parameter starts with '('
            # - payload starts with ':'
            # - block is unclosed and abandoned
            while declaration_i < input_len:
                next_token = _special_tokens_pattern.search(input_str, declaration_i)
                if next_token is None:
                    # unclosed block, take rest as declaration for reconstruction
                    declaration += input_str[declaration_i:]
                    declaration_i = input_len
                else:
                    next_token_pos = next_token.start()
                    declaration += input_str[declaration_i:next_token_pos]
                    char = input_str[next_token_pos]
                    declaration_i = next_token_pos + 1
                    if char == BRACE_OPEN:
                        if input_str[next_token_pos - 1] != BACKSLASH:
                            block_depth += 1
                        declaration += char
                    elif char == BRACE_CLOSE:
                        is_escaped = input_str[next_token_pos - 1] == BACKSLASH
                        if block_depth == 1:
                            if is_escaped:
                                declaration += char
                            else:
                                _nodes.append(
                                    Node.block(
                                        declaration=declaration,
                                        parameter=(
                                            parameter if found_param_section else None
                                        ),
                                        payload=(
                                            payload if found_payload_section else None
                                        ),
                                    ),
                                )
                                block_state = None
                                break
                        else:
                            if not is_escaped:
                                block_depth -= 1
                            declaration += char
                    elif char == PAREN_OPEN:
                        paren_depth += 1
                        if block_depth == 1:
                            found_param_section = True
                            block_state = transition_state(
                                block_state,
                                ParseState.IN_PARAMETER,
                            )
                            break
                        declaration += char
                    elif char == PAREN_CLOSE:
                        declaration += char
                        if paren_depth > 0:
                            paren_depth -= 1
                    elif char == COLON:
                        if block_depth == 1:
                            found_payload_section = True
                            block_state = transition_state(
                                block_state,
                                ParseState.IN_PAYLOAD,
                            )
                            break
                        declaration += char
                    else:
                        raise ValueError(
                            f"Unknown special char {char!r} in IN_DECLARATION",
                        )
            i = declaration_i - 1

        elif block_state is ParseState.IN_PARAMETER:
            parameter_i = i
            # inner loop until one of two things occurs:
            # 1) the parameter section ends (and we hand back to the outer loop)
            # 2) block is unclosed & abandoned
            while parameter_i < input_len:
                next_token = _special_tokens_no_colon_pattern.search(
                    input_str,
                    parameter_i,
                )
                if next_token is None:
                    # unclosed block, take rest as parameter for reconstruction
                    parameter += input_str[parameter_i:]
                    parameter_i = input_len
                else:
                    next_token_pos = next_token.start()
                    parameter += input_str[parameter_i:next_token_pos]
                    char = input_str[next_token_pos]
                    parameter_i = next_token_pos + 1

                    if char == BRACE_OPEN:
                        is_escaped = input_str[next_token_pos - 1] == BACKSLASH
                        if not is_escaped:
                            block_depth += 1
                        parameter += char
                    elif char == BRACE_CLOSE:
                        is_escaped = input_str[next_token_pos - 1] == BACKSLASH
                        if block_depth == 1:
                            if is_escaped:
                                parameter += char
                            else:
                                # invalid block
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
                                break
                        else:
                            if not is_escaped:
                                block_depth -= 1
                            parameter += char
                    elif char == PAREN_OPEN:
                        paren_depth += 1
                        parameter += char
                    elif char == PAREN_CLOSE:
                        paren_depth -= 1
                        if paren_depth == 0:
                            block_state = transition_state(
                                block_state,
                                ParseState.POST_PARAMETER,
                            )
                            break
                        parameter += char
                    else:
                        raise ValueError(
                            f"Unknown special char {char!r} in IN_PARAMETER",
                        )

            i = parameter_i - 1  # hand index back to outer loop

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
            payload_i = i
            while payload_i < input_len:
                # inner loop until one of two things occurs:
                # 1) the block ends (and we hand back to the outer loop)
                # 2) block is unclosed & abandoned
                next_token = _braces_only_pattern.search(input_str, payload_i)
                if next_token is None:
                    # unclosed block, take rest as payload for reconstruction
                    payload += input_str[payload_i:]
                    payload_i = input_len
                else:
                    next_brace_pos = next_token.start()
                    payload += input_str[payload_i:next_brace_pos]
                    char = input_str[next_brace_pos]
                    is_escaped = (
                        next_brace_pos > 0
                        and input_str[next_brace_pos - 1] == BACKSLASH
                    )
                    payload_i = next_brace_pos + 1

                    if char == BRACE_OPEN:
                        if not is_escaped:
                            block_depth += 1
                        payload += char
                    elif char == BRACE_CLOSE:
                        if block_depth == 1:
                            if is_escaped:
                                payload += char
                            else:
                                _nodes.append(
                                    Node.block(
                                        declaration=declaration,
                                        parameter=(
                                            parameter if found_param_section else None
                                        ),
                                        payload=(
                                            payload if found_payload_section else None
                                        ),
                                    ),
                                )
                                block_state = None
                                break  # block finished, exit inner loop to continue
                        else:
                            if not is_escaped:
                                block_depth -= 1
                            payload += char

                    else:
                        raise ValueError(f"Unknown special char {char!r} in IN_PAYLOAD")

            i = payload_i - 1  # hand back index value to outer loop
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

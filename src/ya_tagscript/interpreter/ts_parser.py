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
    pending_start = 0
    section_start = 0
    i = 0
    input_len = len(input_str)

    # initial block data
    block_state: ParseState | None = None
    declaration: str = ""
    parameter: str | None = None
    block_depth: int = 0
    paren_depth: int = 0

    # region processing loop
    # this is an extremely hot loop
    while i < input_len:
        char = input_str[i]

        if block_state is None:
            if char != BRACE_OPEN:
                # fast path for 0-level text chars
                i = input_str.find(BRACE_OPEN, i)
                if i == -1:
                    i = input_len
                continue
            else:  # char == BRACE_OPEN
                is_escaped = i > 0 and input_str[i - 1] == BACKSLASH
                if not is_escaped:
                    if i > pending_start:
                        _nodes.append(Node.text(text_value=input_str[pending_start:i]))
                    pending_start = i
                    block_state = ParseState.EXPECTING_DECLARATION
                    block_depth = 1
                    parameter = None
                    paren_depth = 0

        elif block_state is ParseState.EXPECTING_DECLARATION:
            # EXPECTING_DECLARATION is special:
            # - previous char _must_ have been "{" at 0-depth for block start
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
            elif char == BRACE_CLOSE:
                # state guarantees: previous char is "{" and block_depth == 1
                block_state = None
            elif char == PAREN_OPEN:
                paren_depth += 1
                block_state = transition_state(block_state, ParseState.IN_DECLARATION)
            elif char == PAREN_CLOSE:
                block_state = transition_state(block_state, ParseState.IN_DECLARATION)
                # state guarantee: paren_depth == 0, so can't decrement depth
            else:
                # covers BACKSLASH, COLON, any other char
                block_state = transition_state(block_state, ParseState.IN_DECLARATION)

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
                    declaration_i = input_len
                else:
                    next_token_pos = next_token.start()
                    char = input_str[next_token_pos]
                    declaration_i = next_token_pos + 1
                    if char == BRACE_OPEN:
                        if input_str[next_token_pos - 1] != BACKSLASH:
                            block_depth += 1
                    elif char == BRACE_CLOSE:
                        is_escaped = input_str[next_token_pos - 1] == BACKSLASH
                        if block_depth == 1:
                            if not is_escaped:
                                _nodes.append(
                                    Node.block(
                                        declaration=input_str[
                                            pending_start + 1 : next_token_pos
                                        ],
                                        parameter=None,
                                        payload=None,
                                    ),
                                )
                                pending_start = declaration_i
                                block_state = None
                                break
                        elif not is_escaped:
                            block_depth -= 1
                    elif char == PAREN_OPEN:
                        paren_depth += 1
                        if block_depth == 1:
                            declaration = input_str[pending_start + 1 : next_token_pos]
                            section_start = declaration_i
                            block_state = transition_state(
                                block_state,
                                ParseState.IN_PARAMETER,
                            )
                            break
                    elif char == PAREN_CLOSE:
                        if paren_depth > 0:
                            paren_depth -= 1
                    elif char == COLON:
                        if block_depth == 1:
                            declaration = input_str[pending_start + 1 : next_token_pos]
                            section_start = declaration_i
                            block_state = transition_state(
                                block_state,
                                ParseState.IN_PAYLOAD,
                            )
                            break
                    else:
                        raise ValueError(
                            f"Unknown special char {char!r} in IN_DECLARATION",
                        )
            i = declaration_i - 1  # hand back index value to outer loop

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
                    parameter_i = input_len
                else:
                    next_token_pos = next_token.start()
                    char = input_str[next_token_pos]
                    parameter_i = next_token_pos + 1

                    if char == BRACE_OPEN:
                        is_escaped = input_str[next_token_pos - 1] == BACKSLASH
                        if not is_escaped:
                            block_depth += 1
                    elif char == BRACE_CLOSE:
                        is_escaped = input_str[next_token_pos - 1] == BACKSLASH
                        if block_depth == 1:
                            if not is_escaped:
                                # invalid block: abandon
                                block_state = None
                                break
                        elif not is_escaped:
                            block_depth -= 1
                    elif char == PAREN_OPEN:
                        paren_depth += 1
                    elif char == PAREN_CLOSE:
                        paren_depth -= 1
                        if paren_depth == 0:
                            parameter = input_str[section_start:next_token_pos]
                            block_state = transition_state(
                                block_state,
                                ParseState.POST_PARAMETER,
                            )
                            break
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
                        parameter=parameter,
                        payload=None,
                    ),
                )
                pending_start = i + 1
                block_state = None
            elif char == COLON and block_depth == 1:
                section_start = i + 1
                block_state = transition_state(block_state, ParseState.IN_PAYLOAD)
            else:
                # by state guarantee
                # covers BRACE_OPEN, BRACE_CLOSE (higher depth), PAREN_OPEN,
                # PAREN_CLOSE, COLON (higher depth), BACKSLASH, any other char
                # only colon or pop is allowed here, abort the block entirely
                block_state = None

        elif block_state is ParseState.IN_PAYLOAD:
            payload_i = i
            # inner loop until one of two things occurs:
            # 1) the block ends (and we hand back to the outer loop)
            # 2) block is unclosed & abandoned
            while payload_i < input_len:
                next_token = _braces_only_pattern.search(input_str, payload_i)
                if next_token is None:
                    # unclosed block, take rest as payload for reconstruction
                    payload_i = input_len
                else:
                    next_brace_pos = next_token.start()
                    char = input_str[next_brace_pos]
                    is_escaped = input_str[next_brace_pos - 1] == BACKSLASH
                    payload_i = next_brace_pos + 1

                    if char == BRACE_OPEN:
                        if not is_escaped:
                            block_depth += 1
                    elif char == BRACE_CLOSE:
                        if block_depth == 1:
                            if not is_escaped:
                                _nodes.append(
                                    Node.block(
                                        declaration=declaration,
                                        parameter=parameter,
                                        payload=input_str[section_start:next_brace_pos],
                                    ),
                                )
                                pending_start = payload_i
                                block_state = None
                                break  # block finished, exit inner loop to continue
                        elif not is_escaped:
                            block_depth -= 1
                    else:
                        raise ValueError(f"Unknown special char {char!r} in IN_PAYLOAD")

            i = payload_i - 1  # hand back index value to outer loop

        else:
            assert_never(block_state)

        i += 1
    # endregion end of processing loop

    # Handle any remaining text or unclosed blocks
    if pending_start < input_len:
        _nodes.append(Node.text(text_value=input_str[pending_start:]))

    return _nodes

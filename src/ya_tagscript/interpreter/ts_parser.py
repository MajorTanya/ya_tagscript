import logging

from ya_tagscript.interfaces import NodeABC

from .node import Node
from .parse_state import BlockParseState, ParseState

# this is named "ts_parser" to avoid false positives against the (removed) "parser"
# module in the standard library

_log = logging.getLogger(__name__)


# fmt: off
BACKSLASH   = "\\"
BRACE_OPEN  = "{"
BRACE_CLOSE = "}"
PAREN_OPEN  = "("
PAREN_CLOSE = ")"
COLON       = ":"
# fmt: on


_SPECIAL_TOKENS: set[str] = {
    BACKSLASH,
    BRACE_OPEN,
    BRACE_CLOSE,
    PAREN_OPEN,
    PAREN_CLOSE,
    COLON,
}


class TagScriptParser:

    __slots__ = ("_nodes", "_state", "_text_buffer")

    def __init__(self) -> None:
        self._nodes: list[NodeABC] = []
        self._state: BlockParseState | None = None
        self._text_buffer: str = ""

    def parse(self, input_str: str) -> list[NodeABC]:
        """Converts a string into a list of Nodes and handling nested blocks as text"""
        self._nodes = []
        self._state = None
        self._text_buffer = ""
        i = 0
        input_len = len(input_str)
        special_chars = _SPECIAL_TOKENS

        # region processing loop
        # this is an extremely hot loop so there are additional local references to
        # instance attributes in order to squeeze a bit more performance from the
        # parser
        char = ""
        while i < input_len:
            previous_char = char
            char = input_str[i]
            block: BlockParseState | None = self._state
            current_state = block.state if block is not None else None

            if block is None and char not in special_chars:
                # fast path for of 0-level text chars
                start = i
                while i < input_len and input_str[i] not in special_chars:
                    i += 1
                text = input_str[start:i]
                self._text_buffer += text
                continue

            try:
                if char == BRACE_OPEN:
                    # region Opening brace handling
                    if block is None or current_state is None:
                        if previous_char == BACKSLASH:
                            # escaped, don't start block
                            self._text_buffer += char
                            i += 1
                            continue
                        self._flush_text_buffer()
                        self._state = BlockParseState(
                            state=ParseState.EXPECTING_DECLARATION,
                            block_depth=1,
                        )
                        i += 1
                        continue

                    if previous_char != BACKSLASH:
                        block.block_depth += 1

                    if current_state == ParseState.EXPECTING_DECLARATION:
                        block.transition_state(ParseState.IN_DECLARATION)
                        block.declaration = char
                    elif current_state == ParseState.IN_DECLARATION:
                        if block.declaration is None:
                            block.declaration = char
                        else:
                            block.declaration += char
                    elif current_state == ParseState.IN_PARAMETER:
                        if block.parameter is None:
                            block.parameter = char
                        else:
                            block.parameter += char
                    elif current_state == ParseState.IN_PAYLOAD:
                        if block.payload is None:
                            block.payload = char
                        else:
                            block.payload += char
                    elif current_state == ParseState.POST_PARAMETER:
                        # only colon or pop is allowed here, abort the block entirely
                        self._text_buffer += _reconstruct_partial_block(block)
                        self._text_buffer += char
                        self._state = None
                    # endregion Opening brace handling

                elif char == BRACE_CLOSE:
                    # region Closing brace handling
                    if block is None or current_state is None:
                        self._text_buffer += char
                        i += 1
                        continue
                    elif block.block_depth == 1:
                        if previous_char == BACKSLASH:
                            if current_state == ParseState.IN_DECLARATION:
                                if block.declaration is None:
                                    block.declaration = char
                                else:
                                    block.declaration += char
                            elif current_state == ParseState.IN_PARAMETER:
                                if block.parameter is None:
                                    block.parameter = char
                                else:
                                    block.parameter += char
                            elif current_state == ParseState.IN_PAYLOAD:
                                if block.payload is None:
                                    block.payload = char
                                else:
                                    block.payload += char
                            i += 1
                            continue

                        else:
                            if current_state == ParseState.EXPECTING_DECLARATION:
                                # {} found, illegal BLOCK node, treat as TEXT
                                text = BRACE_OPEN + char
                                self._text_buffer += text
                            else:
                                self._nodes.append(block.finalize())
                            self._state = None
                            i += 1
                            continue

                    if previous_char != BACKSLASH:
                        block.block_depth -= 1

                    if current_state == ParseState.EXPECTING_DECLARATION:
                        block.transition_state(ParseState.IN_DECLARATION)
                        block.declaration = char
                    elif current_state == ParseState.IN_DECLARATION:
                        if block.declaration is None:
                            block.declaration = char
                        else:
                            block.declaration += char
                    elif current_state == ParseState.IN_PARAMETER:
                        if block.parameter is None:
                            block.parameter = char
                        else:
                            block.parameter += char
                    elif current_state == ParseState.IN_PAYLOAD:
                        if block.payload is None:
                            block.payload = char
                        else:
                            block.payload += char
                    elif current_state == ParseState.POST_PARAMETER:
                        # only colon or pop is allowed here, abort the block entirely
                        self._text_buffer += _reconstruct_partial_block(block)
                        self._text_buffer += char
                        self._state = None
                    # endregion Closing brace handling

                elif char == PAREN_OPEN:
                    # region Opening paren handling
                    if block is None or current_state is None:
                        self._text_buffer += char
                        i += 1
                        continue

                    block.paren_depth += 1
                    if current_state == ParseState.EXPECTING_DECLARATION:
                        block.transition_state(ParseState.IN_DECLARATION)
                        block.declaration = char
                    elif current_state == ParseState.IN_DECLARATION:
                        if block.block_depth == 1:
                            block.has_parameter_section = True
                            block.transition_state(ParseState.IN_PARAMETER)
                        elif block.declaration is None:
                            block.declaration = char
                        else:
                            block.declaration += char
                    elif current_state == ParseState.IN_PARAMETER:
                        if block.parameter is None:
                            block.parameter = char
                        else:
                            block.parameter += char
                    elif current_state == ParseState.IN_PAYLOAD:
                        if block.payload is None:
                            block.payload = char
                        else:
                            block.payload += char
                    elif current_state == ParseState.POST_PARAMETER:
                        # only colon or pop is allowed here, abort the block entirely
                        self._text_buffer += _reconstruct_partial_block(block)
                        self._text_buffer += char
                        self._state = None
                    # endregion Opening paren handling

                elif char == PAREN_CLOSE:
                    # region Closing paren handling
                    if block is None or current_state is None:
                        self._text_buffer += char
                        i += 1
                        continue

                    if current_state == ParseState.EXPECTING_DECLARATION:
                        block.transition_state(ParseState.IN_DECLARATION)
                        block.declaration = char
                    elif current_state == ParseState.IN_DECLARATION:
                        if block.declaration is None:
                            block.declaration = char
                        else:
                            block.declaration += char
                    elif current_state == ParseState.IN_PARAMETER:
                        if block.paren_depth == 1:
                            block.transition_state(ParseState.POST_PARAMETER)
                        elif block.parameter is None:
                            block.parameter = char
                        else:
                            block.parameter += char
                    elif current_state == ParseState.IN_PAYLOAD:
                        if block.payload is None:
                            block.payload = char
                        else:
                            block.payload += char
                    elif current_state == ParseState.POST_PARAMETER:
                        # only colon or pop is allowed here, abort the block entirely
                        self._text_buffer += _reconstruct_partial_block(block)
                        self._text_buffer += char
                        self._state = None

                    if block.paren_depth != 0:
                        block.paren_depth -= 1
                    # endregion Closing paren handling

                elif char == COLON:
                    # region Colon handling
                    if block is None or current_state is None:
                        self._text_buffer += char
                        i += 1
                        continue

                    if current_state == ParseState.EXPECTING_DECLARATION:
                        block.transition_state(ParseState.IN_DECLARATION)
                        block.declaration = char
                    elif (
                        current_state
                        in (ParseState.IN_DECLARATION, ParseState.POST_PARAMETER)
                        and block.block_depth == 1
                    ):
                        # end of declaration/post-parameter and beginning of payload
                        block.has_payload_section = True
                        block.transition_state(ParseState.IN_PAYLOAD)
                    elif current_state == ParseState.IN_DECLARATION:
                        if block.declaration is None:
                            block.declaration = char
                        else:
                            block.declaration += char
                    elif current_state == ParseState.IN_PARAMETER:
                        if block.parameter is None:
                            block.parameter = char
                        else:
                            block.parameter += char
                    elif current_state == ParseState.IN_PAYLOAD:
                        if block.payload is None:
                            block.payload = char
                        else:
                            block.payload += char
                    else:
                        self._text_buffer += char
                    # endregion Colon handling

                else:
                    # region Any other char handling (including BACKSLASH)
                    if block is None or current_state is None:
                        # unlikely if not impossible to hit but better safe than sorry
                        # (non-special chars are fast-tracked for None block above)
                        self._text_buffer += char
                        i += 1
                        continue

                    if current_state == ParseState.EXPECTING_DECLARATION:
                        block.transition_state(ParseState.IN_DECLARATION)
                        block.declaration = char
                    elif current_state == ParseState.IN_DECLARATION:
                        if block.declaration is None:
                            block.declaration = char
                        else:
                            block.declaration += char
                    elif current_state == ParseState.IN_PARAMETER:
                        if block.parameter is None:
                            block.parameter = char
                        else:
                            block.parameter += char
                    elif current_state == ParseState.IN_PAYLOAD:
                        if block.payload is None:
                            block.payload = char
                        else:
                            block.payload += char
                    elif current_state == ParseState.POST_PARAMETER:
                        # only colon or pop is allowed here, abort the block entirely
                        self._text_buffer += _reconstruct_partial_block(block)
                        self._text_buffer += char
                        self._state = None
                    # endregion Any other char handling (including BACKSLASH)

            except ValueError as e:
                _log.warning("Invalid state transition encountered: %r", e)
                self._text_buffer += char

            i += 1
        # endregion end of processing loop

        # Handle any remaining text or unclosed blocks
        self._flush_text_buffer()
        if (block := self._state) is not None:
            raw_partial_block = _reconstruct_partial_block(block)
            self._text_buffer += raw_partial_block
            self._flush_text_buffer()
            self._state = None

        return self._nodes

    def _flush_text_buffer(self) -> None:
        """Creates a text node from the current buffer if non-empty."""
        if len(self._text_buffer) > 0:
            self._nodes.append(Node.text(text_value=self._text_buffer))
            self._text_buffer = ""


def _reconstruct_partial_block(block: BlockParseState) -> str:
    """Reconstructs a partial block as text for error recovery."""
    out = BRACE_OPEN
    if block.declaration is not None:
        out += block.declaration
    if block.has_parameter_section:
        out += PAREN_OPEN
        if block.parameter is not None:
            out += block.parameter
        out += PAREN_CLOSE
    if block.has_payload_section:
        out += COLON
        if block.payload is not None:
            out += block.payload
    return out

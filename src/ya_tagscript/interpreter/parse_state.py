from dataclasses import dataclass
from enum import Enum, auto

from ya_tagscript.interfaces import NodeABC

from .node import Node


class ParseState(Enum):
    """
    Represents the current state of parsing within a block.
    States transition in a specific order based on block structure.
    """

    EXPECTING_DECLARATION = auto()  # Initial state when a block starts
    IN_DECLARATION = auto()  # Collecting declaration text
    IN_PARAMETER = auto()  # Between parameter parentheses
    # After completed parameter parentheses, maybe end, maybe payload next
    POST_PARAMETER = auto()
    IN_PAYLOAD = auto()  # After the colon


@dataclass(slots=True)
class BlockParseState:
    """
    Maintains the state of a block being parsed, including its content and current
    parsing state.
    """

    state: ParseState
    block_depth: int = 0
    paren_depth: int = 0
    declaration: list[str] | None = None
    parameter: list[str] | None = None
    has_parameter_section: bool = False  # True if 1-depth () exist, even if empty
    payload: list[str] | None = None
    has_payload_section: bool = False  # True if 1-depth : exists, even if empty

    def finalize(self) -> NodeABC:
        """Convert the parse state into a BLOCK type Node"""
        if self.declaration is None:
            raise ValueError("Cannot finalize BLOCK Node without a declaration.")

        parameter = "".join(self.parameter) if self.parameter is not None else None
        if self.has_parameter_section and parameter is None:
            parameter = ""

        payload = "".join(self.payload) if self.payload is not None else None
        if self.has_payload_section and payload is None:
            payload = ""

        node = Node.block(
            declaration="".join(self.declaration),
            parameter=parameter,
            payload=payload,
        )
        return node

    def transition_state(
        self,
        next_state: ParseState,
    ) -> None:
        """
        Attempts to transition the block's state to the next state.
        Raises ValueError if the transition is invalid.

        Valid transitions are:

            - EXPECTING_DECLARATION -> IN_DECLARATION (on text)
            - IN_DECLARATION -> IN_PARAMETER (on opening parenthesis)
            - IN_DECLARATION -> IN_PAYLOAD (on colon)
            - IN_PARAMETER -> POST_PARAMETER (on closing parenthesis)
            - POST_PARAMETER -> IN_PAYLOAD (on colon)

        Note:

            - IN_PAYLOAD has no valid target state because the only way out is to
                finalize the block.
            - EXPECTING_DECLARATION can transition to the base None state if the tokens
                are "{}"
        """
        if (
            self.state == ParseState.EXPECTING_DECLARATION
            and next_state == ParseState.IN_DECLARATION
        ):
            self.state = next_state

        elif self.state == ParseState.IN_DECLARATION and (
            next_state == ParseState.IN_PARAMETER or next_state == ParseState.IN_PAYLOAD
        ):
            self.state = next_state

        elif (
            self.state == ParseState.IN_PARAMETER
            and next_state == ParseState.POST_PARAMETER
        ):
            self.state = next_state

        elif (
            self.state == ParseState.POST_PARAMETER
            and next_state == ParseState.IN_PAYLOAD
        ):
            self.state = next_state

        else:
            raise ValueError(f"Invalid state transition: {self.state} -> {next_state}")

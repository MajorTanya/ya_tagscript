from dataclasses import dataclass
from enum import Enum, auto

from .node import Node
from ..interfaces import NodeABC


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


VALID_TRANSITIONS: dict[int, frozenset[ParseState]] = {
    ParseState.EXPECTING_DECLARATION.value: frozenset({ParseState.IN_DECLARATION}),
    ParseState.IN_DECLARATION.value: frozenset(
        {ParseState.IN_PARAMETER, ParseState.IN_PAYLOAD},
    ),
    ParseState.IN_PARAMETER.value: frozenset({ParseState.POST_PARAMETER}),
    ParseState.POST_PARAMETER.value: frozenset(
        {ParseState.IN_PAYLOAD},
    ),  # Or pop (not a state)
    ParseState.IN_PAYLOAD.value: frozenset(),  # Only pop gets out of payload
}


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
        if not next_state in VALID_TRANSITIONS.get(self.state.value, frozenset()):
            raise ValueError(f"Invalid state transition: {self.state} -> {next_state}")
        self.state = next_state

from enum import Enum, auto
from typing import Literal, overload


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


@overload
def transition_state(
    current_state: ParseState,
    next_state: Literal[ParseState.IN_DECLARATION],
) -> Literal[ParseState.IN_DECLARATION]: ...


@overload
def transition_state(
    current_state: ParseState,
    next_state: Literal[ParseState.IN_PARAMETER],
) -> Literal[ParseState.IN_PARAMETER]: ...


@overload
def transition_state(
    current_state: ParseState,
    next_state: Literal[ParseState.POST_PARAMETER],
) -> Literal[ParseState.POST_PARAMETER]: ...


@overload
def transition_state(
    current_state: ParseState,
    next_state: Literal[ParseState.IN_PAYLOAD],
) -> Literal[ParseState.IN_PAYLOAD]: ...


def transition_state(
    current_state: ParseState,
    next_state: ParseState,
) -> Literal[
    ParseState.IN_DECLARATION,
    ParseState.IN_PARAMETER,
    ParseState.POST_PARAMETER,
    ParseState.IN_PAYLOAD,
]:
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
        current_state is ParseState.EXPECTING_DECLARATION
        and next_state is ParseState.IN_DECLARATION
    ):
        return next_state

    elif current_state is ParseState.IN_DECLARATION and (
        next_state is ParseState.IN_PARAMETER or next_state is ParseState.IN_PAYLOAD
    ):
        return next_state

    elif (
        current_state is ParseState.IN_PARAMETER
        and next_state is ParseState.POST_PARAMETER
    ):
        return next_state

    elif (
        current_state is ParseState.POST_PARAMETER
        and next_state is ParseState.IN_PAYLOAD
    ):
        return next_state

    else:
        raise ValueError(f"Invalid state transition: {current_state} -> {next_state}")

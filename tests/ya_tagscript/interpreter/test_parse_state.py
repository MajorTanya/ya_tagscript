import pytest

from ya_tagscript.interpreter.parse_state import ParseState, transition_state


def test_invalid_state_transition_raises():
    state = ParseState.EXPECTING_DECLARATION
    with pytest.raises(
        ValueError,
        match="Invalid state transition: ParseState.EXPECTING_DECLARATION -> ParseState.IN_PAYLOAD",
    ):
        # noinspection bad-argument-type
        transition_state(  # pyright: ignore[reportCallIssue]
            state,
            ParseState.IN_PAYLOAD,  # pyright: ignore[reportArgumentType]
        )


@pytest.mark.parametrize(
    ("start_state", "target_state"),
    (
        (ParseState.EXPECTING_DECLARATION, ParseState.IN_DECLARATION),
        (ParseState.IN_DECLARATION, ParseState.IN_PARAMETER),
        (ParseState.IN_DECLARATION, ParseState.IN_PAYLOAD),
        (ParseState.IN_PARAMETER, ParseState.POST_PARAMETER),
        (ParseState.POST_PARAMETER, ParseState.IN_PAYLOAD),
    ),
)
def test_transition_state(
    start_state: ParseState,
    target_state: ParseState,
):
    # type inspection is very unhappy
    # noinspection bad-argument-type
    new_state = transition_state(  # pyright: ignore[reportCallIssue]
        start_state,  # pyright: ignore [reportArgumentType]
        target_state,  # pyright: ignore [reportArgumentType]
    )
    assert new_state is target_state

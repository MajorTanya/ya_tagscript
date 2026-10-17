import pytest

from ya_tagscript.interpreter.parse_state import ParseState, transition_state


def test_invalid_state_transition_raises():
    state = ParseState.EXPECTING_DECLARATION
    with pytest.raises(
        ValueError,
        match="Invalid state transition: ParseState.EXPECTING_DECLARATION -> ParseState.IN_PAYLOAD",
    ):
        transition_state(state, ParseState.IN_PAYLOAD)


def test_expecting_declaration_can_transition_to_in_declaration():
    state = ParseState.EXPECTING_DECLARATION
    new_state = transition_state(state, ParseState.IN_DECLARATION)
    assert new_state == ParseState.IN_DECLARATION


def test_in_declaration_can_transition_to_in_parameter():
    state = ParseState.IN_DECLARATION
    new_state = transition_state(state, ParseState.IN_PARAMETER)
    assert new_state == ParseState.IN_PARAMETER


def test_in_declaration_can_transition_to_in_payload():
    state = ParseState.IN_DECLARATION
    new_state = transition_state(state, ParseState.IN_PAYLOAD)
    assert new_state == ParseState.IN_PAYLOAD


def test_in_parameter_can_transition_to_post_parameter():
    state = ParseState.IN_PARAMETER
    new_state = transition_state(state, ParseState.POST_PARAMETER)
    assert new_state == ParseState.POST_PARAMETER


def test_post_parameter_can_transition_to_in_payload():
    state = ParseState.POST_PARAMETER
    new_state = transition_state(state, ParseState.IN_PAYLOAD)
    assert new_state == ParseState.IN_PAYLOAD

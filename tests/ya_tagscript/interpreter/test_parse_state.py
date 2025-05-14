import pytest

from ya_tagscript.interpreter.parse_state import BlockParseState, ParseState


def test_missing_declaration_in_finalize_raises():
    state = BlockParseState(ParseState.IN_DECLARATION, declaration=None)
    with pytest.raises(
        ValueError,
        match="Cannot finalize BLOCK Node without a declaration.",
    ):
        state.finalize()


def test_invalid_state_transition_raises():
    state = BlockParseState(ParseState.EXPECTING_DECLARATION)
    with pytest.raises(
        ValueError,
        match="Invalid state transition: ParseState.EXPECTING_DECLARATION -> ParseState.IN_PAYLOAD",
    ):
        state.transition_state(ParseState.IN_PAYLOAD)


def test_expecting_declaration_can_transition_to_in_declaration():
    state = BlockParseState(ParseState.EXPECTING_DECLARATION)
    assert state.state == ParseState.EXPECTING_DECLARATION
    state.transition_state(ParseState.IN_DECLARATION)
    assert state.state == ParseState.IN_DECLARATION


def test_in_declaration_can_transition_to_in_parameter():
    state = BlockParseState(ParseState.IN_DECLARATION)
    assert state.state == ParseState.IN_DECLARATION
    state.transition_state(ParseState.IN_PARAMETER)
    assert state.state == ParseState.IN_PARAMETER


def test_in_declaration_can_transition_to_in_payload():
    state = BlockParseState(ParseState.IN_DECLARATION)
    assert state.state == ParseState.IN_DECLARATION
    state.transition_state(ParseState.IN_PAYLOAD)
    assert state.state == ParseState.IN_PAYLOAD


def test_in_parameter_can_transition_to_post_parameter():
    state = BlockParseState(ParseState.IN_PARAMETER)
    assert state.state == ParseState.IN_PARAMETER
    state.transition_state(ParseState.POST_PARAMETER)
    assert state.state == ParseState.POST_PARAMETER


def test_post_parameter_can_transition_to_in_payload():
    state = BlockParseState(ParseState.POST_PARAMETER)
    assert state.state == ParseState.POST_PARAMETER
    state.transition_state(ParseState.IN_PAYLOAD)
    assert state.state == ParseState.IN_PAYLOAD

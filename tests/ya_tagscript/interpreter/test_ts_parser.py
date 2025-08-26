from unittest.mock import MagicMock, patch

import pytest

from ya_tagscript.interpreter.node import Node

# noinspection PyProtectedMember
from ya_tagscript.interpreter.ts_parser import (
    TagScriptParser,
    _reconstruct_partial_block,
)


@pytest.fixture
def parser():
    return TagScriptParser()


@pytest.fixture
def mock_reconstruct_fn():
    with patch(
        "ya_tagscript.interpreter.ts_parser._reconstruct_partial_block",
        wraps=_reconstruct_partial_block,
    ) as mocked_fn:
        yield mocked_fn


def test_unclosed_block_becomes_text(
    parser: TagScriptParser,
    mock_reconstruct_fn: MagicMock,
):
    input_str = "{{"
    nodes = parser.parse(input_str)
    mock_reconstruct_fn.assert_called_once()
    assert nodes == [Node.text(text_value="{{")]


def test_empty_block_becomes_text(
    parser: TagScriptParser,
):
    input_str = "{}"
    nodes = parser.parse(input_str)
    assert nodes == [Node.text(text_value="{}")]


def test_single_closing_brace_is_text(
    parser: TagScriptParser,
):
    input_str = "}"
    nodes = parser.parse(input_str)
    assert nodes == [Node.text(text_value="}")]


def test_nested_block_in_declaration_stays_raw_in_declaration(
    parser: TagScriptParser,
):
    input_str = "{hello{something}}"
    nodes = parser.parse(input_str)
    assert nodes == [
        Node.block(declaration="hello{something}", parameter=None, payload=None),
    ]


def test_fully_nested_declaration_becomes_block_with_single_nested_declaration(
    parser: TagScriptParser,
):
    input_str = "{{nest}}"
    nodes = parser.parse(input_str)
    assert nodes == [Node.block(declaration="{nest}", parameter=None, payload=None)]


def test_string_after_finished_param_section_causes_rejection_to_text(
    parser: TagScriptParser,
):
    input_str = "{dec(para)what:payl}{dec}"
    nodes = parser.parse(input_str)
    assert nodes == [
        Node.text(text_value="{dec(para)what:payl}"),
        Node.block(declaration="dec", parameter=None, payload=None),
    ]


def test_opening_paren_after_finished_param_section_causes_rejection_to_text(
    parser: TagScriptParser,
):
    input_str = "{dec(para)(:payl}"
    nodes = parser.parse(input_str)
    assert nodes == [
        Node.text(text_value="{dec(para)(:payl}"),
    ]


def test_closing_paren_after_finished_param_section_causes_rejection_to_text(
    parser: TagScriptParser,
):
    input_str = "{dec(para)):payl}"
    nodes = parser.parse(input_str)
    assert nodes == [
        Node.text(text_value="{dec(para)):payl}"),
    ]


def test_block_after_finished_param_section_causes_rejection_to_text(
    parser: TagScriptParser,
):
    input_str = "{dec(para){sneaky?}:payl}"
    nodes = parser.parse(input_str)
    assert nodes == [Node.text(text_value="{dec(para){sneaky?}:payl}")]


def test_nested_block_with_param_does_not_cause_outer_block_to_have_param(
    parser: TagScriptParser,
):
    input_str = "{dec{nest(para)}}"
    nodes = parser.parse(input_str)
    assert nodes == [
        Node.block(declaration="dec{nest(para)}", parameter=None, payload=None),
    ]


def test_param_with_nested_paren_section_stays_balanced(
    parser: TagScriptParser,
):
    input_str = "{dec((para)):payl}"
    nodes = parser.parse(input_str)
    assert nodes == [Node.block(declaration="dec", parameter="(para)", payload="payl")]


def test_zero_depth_paren_pairs_stay_text(
    parser: TagScriptParser,
):
    input_str = "(here's a thing){block(para)}"
    nodes = parser.parse(input_str)
    assert nodes == [
        Node.text(text_value="(here's a thing)"),
        Node.block(declaration="block", parameter="para", payload=None),
    ]


def test_closing_paren_in_declaration_stays_in_declaration(
    parser: TagScriptParser,
):
    input_str = "{block)(para):payl}"
    nodes = parser.parse(input_str)
    assert nodes == [Node.block(declaration="block)", parameter="para", payload="payl")]


def test_colon_at_start_of_declaration_stays_in_declaration(
    parser: TagScriptParser,
):
    input_str = "{:weird(para):payl}"
    nodes = parser.parse(input_str)
    assert nodes == [Node.block(declaration=":weird", parameter="para", payload="payl")]


def test_param_pairs_in_payload_stay_in_payload(
    parser: TagScriptParser,
):
    input_str = "{wei:rd(para):payl}"
    nodes = parser.parse(input_str)
    assert nodes == [
        Node.block(declaration="wei", parameter=None, payload="rd(para):payl"),
    ]


def test_block_in_text_are_parsed_correctly(
    parser: TagScriptParser,
):
    input_str = "hello world{block}"
    nodes = parser.parse(input_str)
    assert nodes == [
        Node.text(text_value="hello world"),
        Node.block(declaration="block", parameter=None, payload=None),
    ]


def test_incomplete_block_becomes_text(
    parser: TagScriptParser,
):
    input_str = "{dec(para):payl"
    nodes = parser.parse(input_str)
    assert nodes == [Node.text(text_value=input_str)]


def test_incomplete_block_with_empty_payload_becomes_text(
    parser: TagScriptParser,
):
    input_str = "{dec():"
    nodes = parser.parse(input_str)
    assert nodes == [Node.text(text_value=input_str)]


def test_param_pairs_at_start_of_declaration_stay_in_declaration(
    parser: TagScriptParser,
):
    input_str = "{(hi)}"
    nodes = parser.parse(input_str)
    assert nodes == [Node.block(declaration="(hi)", parameter=None, payload=None)]


def test_closing_paren_at_start_of_declaration_stays_in_declaration(
    parser: TagScriptParser,
):
    input_str = "{)weird}"
    nodes = parser.parse(input_str)
    assert nodes == [Node.block(declaration=")weird", parameter=None, payload=None)]


def test_closing_paren_before_param_section_stays_in_declaration(
    parser: TagScriptParser,
):
    input_str = "{dec)(param):payl}"
    nodes = parser.parse(input_str)
    assert nodes == [Node.block(declaration="dec)", parameter="param", payload="payl")]


def test_escaped_opening_brace_results_in_text_node(
    parser: TagScriptParser,
):
    input_str = "\\{dec(param):payl}"
    nodes = parser.parse(input_str)
    assert nodes == [Node.text(text_value=input_str)]


def test_escaped_closing_brace_does_not_finalize_block_early(
    parser: TagScriptParser,
):
    input_str = "{dec\\}(par):payl}"
    nodes = parser.parse(input_str)
    assert nodes == [
        Node.block(declaration="dec\\}", parameter="par", payload="payl"),
    ]


def test_escaped_braces_in_payload_dont_finish_the_block_and_stay_in_payload(
    parser: TagScriptParser,
):
    input_str = "{dec(param):payl\\}}"
    nodes = parser.parse(input_str)
    assert nodes == [
        Node.block(declaration="dec", parameter="param", payload="payl\\}"),
    ]


def test_escaped_brace_pair_across_declaration_and_param_section_stay_in_each_and_dont_turn_into_block(
    parser: TagScriptParser,
):
    input_str = "{d\\{ec(para\\}m):payl}"
    nodes = parser.parse(input_str)
    assert nodes == [
        Node.block(declaration="d\\{ec", parameter="para\\}m", payload="payl"),
    ]


def test_escaped_brace_pair_within_param_section_stays_in_param_without_becoming_a_block(
    parser: TagScriptParser,
):
    input_str = "{dec:\\{{var\\}}}{second_dec}"
    nodes = parser.parse(input_str)
    assert nodes == [
        Node.block(declaration="dec", parameter=None, payload="\\{{var\\}}"),
        Node.block(declaration="second_dec", parameter=None, payload=None),
    ]

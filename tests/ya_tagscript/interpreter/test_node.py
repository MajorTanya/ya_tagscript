import pytest

from ya_tagscript.interfaces.nodeabc import NodeType
from ya_tagscript.interpreter.node import Node


def test_text_cls_method_works_as_text_node_constructor():
    method_node = Node.text(text_value="my text value")
    constructed_node = Node(
        type=NodeType.TEXT,
        text_value="my text value",
        declaration=None,
        parameter=None,
        payload=None,
    )
    assert constructed_node.type == method_node.type
    assert constructed_node.text_value == method_node.text_value
    assert constructed_node.declaration == method_node.declaration
    assert constructed_node.parameter == method_node.parameter
    assert constructed_node.payload == method_node.payload
    assert constructed_node.output == method_node.output


def test_block_cls_method_works_as_block_node_constructor():
    method_node = Node.block(declaration="dec", parameter="param", payload="pay")
    constructed_node = Node(
        type=NodeType.BLOCK,
        declaration="dec",
        parameter="param",
        payload="pay",
        text_value=None,
    )
    assert constructed_node.type == method_node.type
    assert constructed_node.text_value == method_node.text_value
    assert constructed_node.declaration == method_node.declaration
    assert constructed_node.parameter == method_node.parameter
    assert constructed_node.payload == method_node.payload
    assert constructed_node.output == method_node.output


def test_as_raw_string_raises_when_declaration_is_missing_in_block_node():
    node = Node.block(declaration=None, parameter=None, payload=None)  # type: ignore
    with pytest.raises(
        ValueError,
        match="Cannot have BLOCK type Node without declaration",
    ):
        node.as_raw_string()


def test_as_raw_string_returns_text_value_for_text_node():
    node = Node.text(text_value="my text")
    assert node.as_raw_string() == "my text"


def test_as_raw_string_returns_empty_string_for_missing_text_for_text_node():
    node = Node.text(text_value=None)  # type: ignore
    assert node.as_raw_string() == ""


def test_as_raw_string_returns_valid_block_for_block_node():
    node = Node.block(declaration="test", parameter="param", payload="payload")
    assert node.as_raw_string() == "{test(param):payload}"


def test_as_raw_string_does_not_include_param_section_for_missing_parameter():
    node = Node.block(declaration="test", parameter=None, payload="test payload")
    assert node.as_raw_string() == "{test:test payload}"


def test_as_raw_string_does_not_include_param_section_for_missing_payload():
    node = Node.block(declaration="test", parameter="test param", payload=None)
    assert node.as_raw_string() == "{test(test param)}"

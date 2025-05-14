from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.AnyBlock(),
        blocks.AssignmentBlock(),
        blocks.CommandBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.AnyBlock()
    assert block._accepted_names == {"any", "or"}


def test_process_method_rejects_missing_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    block = blocks.AnyBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = ""

    block = blocks.AnyBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "     "

    block = blocks.AnyBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "I have to be valid to pass the first check"
    mock_ctx.node.payload = None

    block = blocks.AnyBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "I have to be valid to pass the first check"
    mock_ctx.node.payload = ""

    block = blocks.AnyBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "I have to be valid to pass the first check"
    mock_ctx.node.payload = "     "

    block = blocks.AnyBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_any_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any({args}==hi|{args}==hello|{args}==heyy):Hello {user}!|How rude.}"
    data = {
        "args": adapters.StringAdapter("hi"),
        "user": adapters.StringAdapter("username"),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "Hello username!"


def test_dec_any_docs_example_one_other_choice(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any({args}==hi|{args}==hello|{args}==heyy):Hello {user}!|How rude.}"
    data = {
        "args": adapters.StringAdapter("what's up!"),
        "user": adapters.StringAdapter("username"),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "How rude."


def test_dec_any_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any(1==2|0>1):This is my success case message}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_any_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any(1==1|2<5):|This is my failure case message}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_any_docs_example_four(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{=(msgs):Success msg|Failure msg}{any(1==1|abc!=abc):{msgs}}"
    result = ts_interpreter.process(script).body
    assert result == "Success msg|Failure msg"


def test_dec_any_single_condition(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any(1==2):positive}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_any_no_negative_payload(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any(1==3|1==2|1==0):positive}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_any_empty_conditions_are_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any():positive|negative}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_any_missing_conditions_are_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any:positive|negative}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_any_immune_to_injection(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any({args}==1|{args}==3):pos|neg}"
    data = {"args": adapters.StringAdapter("yes!")}
    result = ts_interpreter.process(script, data).body
    assert result == "neg"


def test_dec_any_parameter_is_interpreted_but_needs_operator_at_zero_depth(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any({my_var}|{other_var}):positive|negative}"
    data = {
        "my_var": adapters.StringAdapter("1==1"),
        "other_var": adapters.StringAdapter("x==y"),
    }
    result = ts_interpreter.process(script, data).body
    # both conditions evaluate to None, and None is not Trues
    assert result == "negative"


def test_dec_any_fully_nested_parameter_fails(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any({my_var}):pos|neg}"
    # these conditions are obviously truthy but the zero-depth separator requirement
    # means this will fail
    data = {"my_var": adapters.StringAdapter("1==1|1<2")}
    result = ts_interpreter.process(script, data).body
    assert result != "pos"


def test_dec_any_parameter_is_interpreted_after_operator_detection(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any({my_var}==2|{my_var}==4):pos|neg}"
    data = {"my_var": adapters.StringAdapter("2")}
    result = ts_interpreter.process(script, data).body
    assert result == "pos"


def test_dec_any_fully_nested_payload_is_considered_success_case_even_with_pipe(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any(1==1|c!=d):{my_var}}"
    data = {"my_var": adapters.StringAdapter("pos|neg")}
    result = ts_interpreter.process(script, data).body
    assert result == "pos|neg"


def test_dec_any_payload_is_interpreted_even_if_partial(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any(1!=1|2>2):{my_var}|fail}"
    data = {"my_var": adapters.StringAdapter("pos")}
    result = ts_interpreter.process(script, data).body
    assert result == "fail"


def test_dec_any_side_effect_avoidance(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{any({args}==123|1!=1):{command:echo password accepted!}|something else}"
    data = {"args": adapters.StringAdapter("blah")}
    response = ts_interpreter.process(script, data)
    assert response.body == "something else"
    assert response.actions.get("commands") is None

from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.AssignmentBlock(),
        blocks.CommandBlock(),
        blocks.IfBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.IfBlock()
    assert block._accepted_names == {"if"}


def test_process_method_rejects_missing_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    block = blocks.IfBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = ""

    block = blocks.IfBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "     "

    block = blocks.IfBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "I have to be valid to pass the first check"
    mock_ctx.node.payload = None

    block = blocks.IfBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "I have to be valid to pass the first check"
    mock_ctx.node.payload = ""

    block = blocks.IfBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "I have to be valid to pass the first check"
    mock_ctx.node.payload = "     "

    block = blocks.IfBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_if_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if({args}==63):You guessed it! The number I was thinking of was 63!|Too {if({args}<63):low|high}, try again.}"
    data = {"args": adapters.StringAdapter("63")}
    result = ts_interpreter.process(script, data).body
    assert result == "You guessed it! The number I was thinking of was 63!"


def test_dec_if_docs_example_one_too_high(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if({args}==63):You guessed it! The number I was thinking of was 63!|Too {if({args}<63):low|high}, try again.}"
    data = {"args": adapters.StringAdapter("73")}
    result = ts_interpreter.process(script, data).body
    assert result == "Too high, try again."


def test_dec_if_docs_example_one_too_low(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if({args}==63):You guessed it! The number I was thinking of was 63!|Too {if({args}<63):low|high}, try again.}"
    data = {"args": adapters.StringAdapter("14")}
    result = ts_interpreter.process(script, data).body
    assert result == "Too low, try again."


def test_dec_if_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if(false):This is my success case message}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_if_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if(true):|This is my failure case message}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_if_docs_example_four(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{=(msgs):Success msg|Failure msg}{if(true):{msgs}}"
    result = ts_interpreter.process(script).body
    assert result == "Success msg|Failure msg"


@pytest.mark.parametrize(
    ("script", "out"),
    (
        pytest.param("{if(1==1):was true|was false}", "was true", id="true"),
        pytest.param("{if(1==2):was true|was false}", "was false", id="false"),
        pytest.param("{if(true):was true|was false}", "was true", id="const_true"),
        pytest.param("{if(false):was true|was false}", "was false", id="const_false"),
        pytest.param("{if(1==1):was true}", "was true", id="true_missing_else"),
        pytest.param("{if(1==2):was true}", "", id="false_missing_else"),
        pytest.param("{if(invalid param):was true|was false}", "", id="invalid"),
        pytest.param("{if():was true}", "{if():was true}", id="missing_cond"),
        pytest.param("{if(true):}", "{if(true):}", id="empty_payload"),
    ),
)
def test_dec_if_basic(
    script: str,
    out: str,
    ts_interpreter: TagScriptInterpreter,
):
    result = ts_interpreter.process(script).body
    assert result == out


def test_dec_if_interpolation_true_condition(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if({my_var}==2):was true|was false}"
    data = {"my_var": adapters.IntAdapter(2)}
    result = ts_interpreter.process(script, data).body
    assert result == "was true"


def test_dec_if_interpolation_false_condition(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if({my_var}==2):was true|was false}"
    data = {"my_var": adapters.IntAdapter(1)}
    result = ts_interpreter.process(script, data).body
    assert result == "was false"


def test_dec_if_nested_if_correct_order(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if({if(2>1):inside was true|inside was false}==inside was true):outside was true|outside was false}"
    result = ts_interpreter.process(script).body
    assert result == "outside was true"


def test_dec_if_immune_to_interpolation_injection(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if({my_var}==value):was true|was false}"
    data = {"my_var": adapters.StringAdapter("user!")}
    result = ts_interpreter.process(script, data).body
    assert result == "was false"


def test_dec_if_immune_to_interpolation_injection_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if({my_var}==user!):was true|was false}"
    data = {"my_var": adapters.StringAdapter("user!")}
    result = ts_interpreter.process(script, data).body
    assert result == "was true"


def test_dec_if_parameter_is_interpreted_but_needs_operator_at_zero_depth(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if({my_var}):was true|was false}"
    data = {"my_var": adapters.StringAdapter("1==1")}
    result = ts_interpreter.process(script, data).body
    assert result == ""


def test_dec_if_parameter_is_interpreted_after_operator_detection(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if(yes=={my_var}):was true|was false}"
    data = {"my_var": adapters.StringAdapter("yes")}
    result = ts_interpreter.process(script, data).body
    assert result == "was true"


def test_dec_if_fully_nested_payload_is_considered_success_case_even_with_pipe(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if(1==1):{my_var}}"
    data = {"my_var": adapters.StringAdapter("pos|neg")}
    result = ts_interpreter.process(script, data).body
    assert result == "pos|neg"


def test_dec_if_payload_is_interpreted_even_if_partial(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if(1==2):{my_var}|fail}"
    data = {"my_var": adapters.StringAdapter("pos")}
    result = ts_interpreter.process(script, data).body
    assert result == "fail"


def test_dec_if_readme_example_side_effect_avoidance(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if({args}==123):{command:echo password accepted!}|something else}"
    data = {"args": adapters.StringAdapter("blah")}
    response = ts_interpreter.process(script, data)
    assert response.body == "something else"
    assert response.actions.get("commands") is None

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.IfBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_string_is_stored(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_str}"
    data = {"my_str": adapters.StringAdapter("hello world")}
    result = ts_interpreter.process(script, data).body
    assert result == "hello world"


def test_empty_payload_returns_full_string(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_str:}"
    data = {"my_str": adapters.StringAdapter("hello world")}
    result = ts_interpreter.process(script, data).body
    assert result == "hello world"


def test_parameter_used_as_index(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_str(2)}"
    data = {"my_str": adapters.StringAdapter("hello world")}
    result = ts_interpreter.process(script, data).body
    assert result == "world"


def test_payload_used_as_splitter(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_str(2):,}"
    data = {"my_str": adapters.StringAdapter("hello,world again")}
    result = ts_interpreter.process(script, data).body
    assert result == "world again"


def test_payload_used_as_splitter_colon(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_str(2)::}"
    data = {"my_str": adapters.StringAdapter("to:you")}
    result = ts_interpreter.process(script, data).body
    assert result == "you"


def test_with_parameter_and_empty_payload_returns_full_string(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_str(2):}"
    data = {"my_str": adapters.StringAdapter("hello world")}
    result = ts_interpreter.process(script, data).body
    assert result == "hello world"


def test_parameter_with_plus(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_str(2+)}"
    data = {"my_str": adapters.StringAdapter("my secret message is here")}
    result = ts_interpreter.process(script, data).body
    assert result == "secret message is here"


def test_parameter_preceded_by_plus(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_str(+2)}"
    data = {"my_str": adapters.StringAdapter("my secret message")}
    result = ts_interpreter.process(script, data).body
    assert result == "my secret"


def test_parameter_plus_in_middle_removed(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_str(1+1)}"  # plus is removed -> "1+1" into "11" into 11 (int) into index 10 (int)
    data = {
        "my_str": adapters.StringAdapter(
            "my secret message is actually very long if you think about it",
        ),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "about"


def test_parameter_plus_in_middle_removed_with_payload(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_str(1+1):,}"  # plus is removed -> "1+1" into "11" into 11 (int) into index 10 (int)
    data = {
        "my_str": adapters.StringAdapter(
            "my,secret,message,is,actually,very,long,if,you,think,about it",
        ),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "about it"


def test_escapes_if_constructed_to_escape(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if({msg}==):provide a message|{msg}}"
    data = {"msg": adapters.StringAdapter("message provided :", should_escape=True)}
    result = ts_interpreter.process(script, data).body
    assert result == "message provided \\:"


def test_does_not_escape_by_default(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if({msg}==):provide a message|{msg}}"
    data = {"msg": adapters.StringAdapter("message provided :")}
    result = ts_interpreter.process(script, data).body
    assert result == "message provided :"


def test_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_string_variable(2)}"
    data = {
        "my_string_variable": adapters.StringAdapter("Hello there. General Kenobi."),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "there."


def test_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_string_variable(3)}"
    data = {
        "my_string_variable": adapters.StringAdapter("Hello there. General Kenobi."),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "General"


def test_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_string_variable(3+)}"
    data = {
        "my_string_variable": adapters.StringAdapter("Hello there. General Kenobi."),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "General Kenobi."


def test_docs_example_four(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_string_variable(+2)}"
    data = {
        "my_string_variable": adapters.StringAdapter("Hello there. General Kenobi."),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "Hello there."


def test_docs_example_five(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_string_variable(2):.}"
    data = {
        "my_string_variable": adapters.StringAdapter("Hello there. General Kenobi."),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "General Kenobi"


def test_docs_example_six(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_string_variable(3):en}"
    data = {
        "my_string_variable": adapters.StringAdapter("Hello there. General Kenobi."),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "obi."

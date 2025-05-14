import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.AssignmentBlock(),
        blocks.DeleteBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.DeleteBlock()
    assert block._accepted_names == {"del", "delete"}


def test_dec_delete_duplicated_uses_dont_matter(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{delete}{delete}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    assert response.actions.get("delete")


def test_dec_delete_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{delete}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    assert response.actions.get("delete")


def test_dec_delete_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{delete(true==true)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    assert response.actions.get("delete")


def test_dec_delete_falsy_param(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{delete(true==false)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    assert not response.actions.get("delete")


def test_dec_delete_nested_parameter_is_parsed_correctly(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{=(second):2}{delete({=(first):1}{first}!={second})}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    assert response.actions.get("delete")


def test_dec_delete_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{delete({myvar})}"
    data = {"myvar": adapters.StringAdapter("true")}
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    assert response.actions.get("delete")

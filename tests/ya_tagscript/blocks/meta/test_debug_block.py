import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.AssignmentBlock(),
        blocks.DebugBlock(),
        blocks.IfBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.DebugBlock()
    assert block._accepted_names == {"debug"}


def test_dec_debug_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{=(something):Hello/World}\n"
        "{=(parsed):{something(1)}}\n"
        "{if({parsed}==Hello):Hello|Bye}\n"
        "{debug}"
    )
    response = ts_interpreter.process(script)
    assert response.body == "Bye"
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {
        "something": "Hello/World",
        "parsed": "Hello/World",
    }


def test_dec_debug_docs_example_one_fix_applied(
    ts_interpreter: TagScriptInterpreter,
):
    # The "fixed" version of the example script
    # (adding missing delimiter to parsed definition)
    script = (
        "{=(something):Hello/World}\n"
        "{=(parsed):{something(1):/}}\n"
        "{if({parsed}==Hello):Hello|Bye}\n"
        "{debug}"
    )
    response = ts_interpreter.process(script)
    assert response.body == "Hello"
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {
        "something": "Hello/World",
        "parsed": "Hello",
    }


def test_dec_debug_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{debug:my_var,another var}"
    data = {
        "my_var": adapters.StringAdapter("my var value"),
        "another var": adapters.StringAdapter("another var value"),
    }
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {
        "my_var": "my var value",
        "another var": "another var value",
    }


def test_dec_debug_include_several_values_with_i_param(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{=(something):Hello/World}\n"
        "{=(parsed):{something(1):/}}\n"
        "{debug(i):something~parsed}"
    )
    response = ts_interpreter.process(script)
    assert response.body == ""
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {
        "something": "Hello/World",
        "parsed": "Hello",
    }


def test_dec_debug_include_with_i_param(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{=(something):Hello/World}\n"
        "{=(parsed):{something(1):/}}\n"
        "{debug(i):something}"
    )
    response = ts_interpreter.process(script)
    assert response.body == ""
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {"something": "Hello/World"}


def test_dec_debug_include_with_inc_param(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{=(something):Hello/World}\n"
        "{=(parsed):{something(1):/}}\n"
        "{debug(inc):something}"
    )
    response = ts_interpreter.process(script)
    assert response.body == ""
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {"something": "Hello/World"}


def test_dec_debug_include_with_include_param(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{=(something):Hello/World}\n"
        "{=(parsed):{something(1):/}}\n"
        "{debug(include):something}"
    )
    response = ts_interpreter.process(script)
    assert response.body == ""
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {"something": "Hello/World"}


def test_dec_debug_exclude_with_e_param(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{=(something):Hello/World}\n"
        "{=(parsed):{something(1):/}}\n"
        "{debug(e):parsed}"
    )
    response = ts_interpreter.process(script)
    assert response.body == ""
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {"something": "Hello/World"}


def test_dec_debug_exclude_with_exc_param(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{=(something):Hello/World}\n"
        "{=(parsed):{something(1):/}}\n"
        "{debug(exc):parsed}"
    )
    response = ts_interpreter.process(script)
    assert response.body == ""
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {"something": "Hello/World"}


def test_dec_debug_exclude_with_exclude_param(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{=(something):Hello/World}\n"
        "{=(parsed):{something(1):/}}\n"
        "{debug(exclude):parsed}"
    )
    response = ts_interpreter.process(script)
    assert response.body == ""
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {"something": "Hello/World"}


def test_dec_debug_include_without_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{=(something):Hello/World}\n"
        "{=(parsed):{something(1):/}}\n"
        "{debug(include)}"
    )
    response = ts_interpreter.process(script)
    assert response.body == "{debug(include)}"


def test_dec_debug_exclude_without_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{=(something):Hello/World}\n"
        "{=(parsed):{something(1):/}}\n"
        "{debug(exclude)}"
    )
    response = ts_interpreter.process(script)
    assert response.body == "{debug(exclude)}"


def test_dec_debug_payload_without_param_is_treated_as_include(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{=(something):Hello/World}\n"
        "{=(parsed):{something(1):/}}\n"
        "{debug:something}"
    )
    response = ts_interpreter.process(script)
    assert response.body == ""
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {"something": "Hello/World"}


def test_dec_debug_payload_without_param_is_treated_as_include_several_values(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{=(something):Hello/World}\n"
        "{=(parsed):{something(1):/}}\n"
        "{debug:something~parsed}"
    )
    response = ts_interpreter.process(script)
    assert response.body == ""
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {
        "something": "Hello/World",
        "parsed": "Hello",
    }


def test_dec_debug_values_with_delimiter_strings_arent_split_up(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{=(first_var):1,2,3,4}\n"
        "{=(my_var):I~My~Me}\n"
        "{=(other_var):You,Me,Them}\n"
        "{debug}"
    )
    response = ts_interpreter.process(script)
    assert response.body == ""
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {
        "first_var": "1,2,3,4",
        "my_var": "I~My~Me",
        "other_var": "You,Me,Them",
    }


def test_dec_debug_if_no_variables_exist_debug_output_is_empty(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{debug}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {}


def test_dec_debug_if_specified_variables_dont_exist_debug_output_is_empty(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{debug:my_var}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {}


def test_dec_debug_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{=(my_var):one}{=(second_var):two}{debug(e):second_var}"
    response = ts_interpreter.process(script)
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {"my_var": "one"}


def test_dec_debug_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{=(my_var):one}{=(second_var):two}{debug:my_var}"
    response = ts_interpreter.process(script)
    debug_dict = response.extra_kwargs.get("debug")
    assert debug_dict is not None
    assert debug_dict == {"my_var": "one"}

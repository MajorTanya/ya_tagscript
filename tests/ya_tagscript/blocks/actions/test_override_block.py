import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.OverrideBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.OverrideBlock()
    assert block._accepted_names == {"override"}


def test_dec_override_no_parameter_means_all_overrides_set(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{override}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    overrides = response.actions.get("overrides")
    assert overrides is not None
    assert overrides == {"admin": True, "mod": True, "permissions": True}


def test_dec_override_admin_parameter_means_admin_override(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{override(admin)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    overrides = response.actions.get("overrides")
    assert overrides is not None
    assert overrides == {"admin": True, "mod": False, "permissions": False}


def test_dec_override_mod_parameter_means_mod_override(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{override(mod)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    overrides = response.actions.get("overrides")
    assert overrides is not None
    assert overrides == {"admin": False, "mod": True, "permissions": False}


def test_dec_override_permissions_parameter_means_permissions_override(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{override(permissions)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    overrides = response.actions.get("overrides")
    assert overrides is not None
    assert overrides == {"admin": False, "mod": False, "permissions": True}


def test_dec_override_other_parameter_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{override(parameter)}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_override_cannot_set_multiple_overrides_in_one_block(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{override(admin,mod)}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_override_multiple_uses_are_combined_properly(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{override(admin)}{override(permissions)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    overrides = response.actions.get("overrides")
    assert overrides is not None
    assert overrides == {"admin": True, "mod": False, "permissions": True}


def test_dec_override_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{override({my_var})}"
    data = {"my_var": adapters.StringAdapter("admin")}
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    overrides = response.actions.get("overrides")
    assert overrides is not None
    assert overrides == {"admin": True, "mod": False, "permissions": False}

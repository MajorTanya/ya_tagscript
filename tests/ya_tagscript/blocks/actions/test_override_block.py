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


@pytest.mark.parametrize(
    ("script", "overrides_out"),
    (
        pytest.param(
            "{override}",
            {"admin": True, "mod": True, "permissions": True},
            id="no_parameter_sets_all_overrides",
        ),
        pytest.param(
            "{override(admin)}",
            {"admin": True, "mod": False, "permissions": False},
            id="admin_parameter_only_sets_admin_override",
        ),
        pytest.param(
            "{override(mod)}",
            {"admin": False, "mod": True, "permissions": False},
            id="mod_parameter_only_sets_mod_override",
        ),
        pytest.param(
            "{override(permissions)}",
            {"admin": False, "mod": False, "permissions": True},
            id="permissions_parameter_only_sets_permissions_override",
        ),
        pytest.param(
            "{override(admin)}{override(mod)}",
            {"admin": True, "mod": True, "permissions": False},
            id="multiple_overrides_are_combined",
        ),
    ),
)
def test_dec_override_valid_settings(
    script: str,
    overrides_out: dict[str, bool],
    ts_interpreter: TagScriptInterpreter,
):
    response = ts_interpreter.process(script)
    assert response.body == ""
    overrides = response.actions.get("overrides")
    assert overrides is not None
    assert overrides == overrides_out


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

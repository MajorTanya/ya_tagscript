from ya_tagscript import TagScriptInterpreter, adapters, blocks


def test_quickstart_example():
    used_blocks = [
        blocks.CaseBlock(),
        blocks.IfBlock(),
        blocks.StrictVariableGetterBlock(),
    ]

    interpreter = TagScriptInterpreter(used_blocks)

    script = "{if({args(1)}==up):{upper:{args(2+)}}|{lower:{args(2+)}}}"

    seeds = {
        "args": adapters.StringAdapter("up hello world"),
    }

    extras = {}

    maximum_characters = 2_000

    response = interpreter.process(
        script,
        seed_variables=seeds,
        extra_kwargs=extras,
        work_limit=maximum_characters,
    )

    assert response.actions == {}
    assert response.extra_kwargs == {}
    # Check that only the seed variables are set
    assert response.variables == seeds
    assert response.body == "HELLO WORLD"

from ya_tagscript import TagScriptInterpreter, adapters, blocks


class MyObject:

    def __init__(self, the_attr: int) -> None:
        self.my_attr = the_attr


def test_nested_blocks_example():
    used_blocks = [
        blocks.AssignmentBlock(),
        blocks.CommentBlock(),
        blocks.IfBlock(),
        blocks.MathBlock(),
        blocks.RangeBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    interpreter = TagScriptInterpreter(used_blocks)

    script = """
{comment:Note that we're using a seed for the range block so we can guarantee the
result (it's 52 for this seed)
also, blocks can have multiline parameters and payloads as you can see (though comment
blocks are simply removed from the output)}

{=(random_number):{range({random-seed}):1-100}}
The totally random number is: {random_number}
{=(calculated):{math:{my object(my_attr)} * {random_number}}}
The random number times our object attribute results in: {calculated}
{if({calculated}>100000):Wow that is huge!|{math:trunc({calculated})} is a pretty neat number}

And to prove that seeding the range block works:
{=(manual_calculation):{math:52 * 1024}}
{if({calculated}=={manual_calculation}):Seeding worked!|😅 Oops! If you get this output line, tell the dev that range seeding broke…}
    """.strip()

    my_object = MyObject(1024)
    seeds = {
        "random-seed": adapters.IntAdapter(13579),
        "my object": adapters.ObjectAdapter(my_object),
    }

    response = interpreter.process(script, seed_variables=seeds)

    assert response.actions == {}
    assert response.extra_kwargs == {}
    assert len(response.variables) == 5

    random_seed_var = response.variables.get("random-seed")
    assert isinstance(random_seed_var, adapters.IntAdapter)
    assert random_seed_var.integer == 13579

    my_object_var = response.variables.get("my object")
    assert isinstance(my_object_var, adapters.ObjectAdapter)
    assert my_object_var.obj == my_object

    random_number_var = response.variables.get("random_number")
    assert isinstance(random_number_var, adapters.StringAdapter)
    assert random_number_var.string == "52"

    calculated_var = response.variables.get("calculated")
    assert isinstance(calculated_var, adapters.StringAdapter)
    assert calculated_var.string == "53248.0"

    manual_calculation_var = response.variables.get("manual_calculation")
    assert isinstance(manual_calculation_var, adapters.StringAdapter)
    assert manual_calculation_var.string == "53248.0"

    assert response.body == (
        "The totally random number is: 52\n\n"
        "The random number times our object attribute results in: 53248.0\n"
        "53248 is a pretty neat number\n\n"
        "And to prove that seeding the range block works:\n\n"
        "Seeding worked!"
    )

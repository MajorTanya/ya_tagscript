from ya_tagscript import TagScriptInterpreter, adapters, blocks


class MyObject:

    def __init__(self, the_attr: int) -> None:
        self.my_attr = the_attr


used_blocks = [
    blocks.AssignmentBlock(),
    blocks.CommentBlock(),
    blocks.IfBlock(),
    blocks.MathBlock(),
    blocks.RangeBlock(),
    blocks.StrictVariableGetterBlock(),
]
interpreter = TagScriptInterpreter(used_blocks)

# This is also a neat demonstration that variable names can use spaces, hyphens, etc.
# in their names (though underscores are probably more readable)

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

seeds = {
    "random-seed": adapters.IntAdapter(13579),
    "my object": adapters.ObjectAdapter(MyObject(1024)),
}

response = interpreter.process(script, seed_variables=seeds)
print(response.body)

# The totally random number is: 52
#
# The random number times our object attribute results in: 53248.0
# 53248 is a pretty neat number
#
# And to prove that seeding the range block works:
#
# Seeding worked!

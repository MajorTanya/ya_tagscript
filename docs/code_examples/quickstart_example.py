from ya_tagscript import TagScriptInterpreter, adapters, blocks

# include all blocks needed for the script(s) used
used_blocks = [
    blocks.CaseBlock(),
    blocks.IfBlock(),
    blocks.StrictVariableGetterBlock(),
]

# supply the blocks to the interpreter
# (this instance can be reused — just call its process method again with the next script)
interpreter = TagScriptInterpreter(used_blocks)

# write/retrieve some TagScript script
script = "{if({args(1)}==up):{upper:{args(2+)}}|{lower:{args(2+)}}}"

# optionally, define seed variables in a dictionary with the appropriate adapters
# defaults to an empty dictionary if not passed to the interpreter
seeds = {
    "args": adapters.StringAdapter("up hello world"),
}

# optionally, define some extra arguments (very few blocks use this)
# these do NOT need to use the adapters
# defaults to an empty dictionary if not passed to the interpreter
extras = {}

# optionally, define a work limit for the interpreter
# defaults to None if not passed to the interpreter (meaning absolutely no limits)
maximum_characters = 2_000

# tell the interpreter to do some work on the script
response = interpreter.process(
    script,
    seed_variables=seeds,
    extra_kwargs=extras,
    work_limit=maximum_characters,
)

# the actions attribute contains actions defined in the script that the client (you)
# should act upon
print(response.actions)

# extras some blocks may have defined
print(response.extra_kwargs)

# this contains all variables that were defined during processing
print(response.variables)

# the body attribute contains the text output
print(response.body)  # HELLO WORLD

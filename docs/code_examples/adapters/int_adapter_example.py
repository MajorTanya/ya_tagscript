from ya_tagscript import TagScriptInterpreter, adapters, blocks

used_blocks = [
    blocks.StrictVariableGetterBlock(),
]
interpreter = TagScriptInterpreter(used_blocks)

script = "His power level is over {level}!!"

seeds = {
    "level": adapters.IntAdapter(9000),
}

response = interpreter.process(script, seed_variables=seeds)
print(response.body)  # His power level is over 9000!!

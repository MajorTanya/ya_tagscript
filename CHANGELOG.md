# Unreleased

*Currently none*

# v1.6.0

- Function names in ``MathBlock`` are now case-insensitive
    - Example: `tan`, `TAN`, `tAn`, etc. all now call the tangent function
    - Should not have any user-facing consequences, since these are matched in an
      already-parsed block body and thus are only text.

# v1.5.0

- Enforce zero-depth requirement for the specially formed attributes of `EmbedBlock`
    - This affects the payloads of ``author``, ``field``, and ``footer``, whose payloads
      must now have a ``|`` at "{term}`zero-depth`" to properly separate their different
      sub-attributes.

# v1.4.3

- Refactor tests to use pytest.parametrize

- Fix accidental dict literal instead of empty set constructor in `BlockABC.will_accept`
    - Should not have had any user-facing consequences since it is just an empty
      fallback

# v1.4.2

- Catch `ParseBaseException` in `MathBlock` instead of `ParseSyntaxException`
    - The approach in [the previous version](#v141) did not suffice.

# v1.4.1

- Reject invalid syntax in `MathBlock`
    - Blocks that contain invalid/unparseable syntax and cause pyparsing to raise a
      `ParseSyntaxException` are now rejected instead of throwing an exception into the
      interpreter

# v1.4.0

- Removed use of `@override` annotations to actually support Python 3.11

# v1.3.2

- Reject division by zero in `MathBlock`
    - Blocks that divide by zero are now rejected instead of throwing an exception into
      the interpreter

# v1.3.1

- Fix copy/paste errors in `EmbedBlock`'s documentation
    - The `field` section contained copy/pasted `footer` text, this has been fixed

# v1.3.0

- Fix undefined guild-specific or global nicknames causing blocks to be rejected
    - For `discord.Member` objects, `MemberAdapter` now falls back to `global_name` if
      `nick` is undefined and further to `name` if `global_name` is also undefined
    - For `discord.User` objects, `MemberAdapter` now falls back to `name` if
      `global_name` is undefined

- Fix an undefined channel topic causing blocks to be rejected
    - `ChannelAdapter` now falls back to an empty string

- Move `PythonBlock` from `blocks.conditional` to `blocks.strings`
    - Never belonged in the `conditional` grouping
    - This should not affect any users since blocks are exported via
      `ya_tagscript.blocks` but if `PythonBlock` was imported from the full path, the
      following change is necessary:
      ```diff
      -from ya_tagscript.blocks.conditional import PythonBlock
      +from ya_tagscript.blocks.strings import PythonBlock
      ```
      or
      ```diff
      -from ya_tagscript.blocks.conditional.python_block import PythonBlock
      +from ya_tagscript.blocks.strings.python_block import PythonBlock
      ```
      but the recommended way remains
      ```diff
      -from ya_tagscript.blocks.conditional import PythonBlock
      +from ya_tagscript.blocks import PythonBlock
      ```

- Fix duplicate spaces between emoji in `ReactBlock` being counted against the emoji
  limit
    - These spaces are now ignored and only the actual strings passed are counted

# v1.2.1

- Make loggers and `TimedeltaBlock.humanize_fn` private values/attributes
    - These are all internal details with no place in the user's code

- Replace `datetime.timezone.utc` with `datetime.UTC`

# v1.2.0

- Allow passing `discord.User` to `MemberAdapter`
    - Allows conveniently passing `ctx.author` to a seed variable `MemberAdapter`, for
      example

- Add ``.. versionchanged`` directives to `CycleBlock` and `ListBlock` regarding the
  [1.1.0](#v110) changes
    - Also re-added both blocks to the "Referenced by" section of the zero-depth
      glossary entry

# v1.1.0

- `CycleBlock` and `ListBlock` no longer have a "{term}`zero-depth`" restriction

# v1.0.0

Full rearchitecture of interpreter released.

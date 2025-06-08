# Unreleased

- Fix undefined guild-specific or global nicknames causing blocks to be rejected
    - For `discord.Member` objects, `MemberAdapter` now falls back to `global_name` if
      `nick` is undefined and further to `name` if `global_name` is also undefined
    - For `discord.User` objects, `MemberAdapter` now falls back to `name` if
      `global_name` is undefined
- Fix an undefined channel topic causing blocks to be rejected
    - `ChannelAdapter` now falls back to an empty string

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

- `CycleBlock` and `ListBlock` no longer have a "zero-depth" restriction

# v1.0.0

Full rearchitecture of interpreter released.

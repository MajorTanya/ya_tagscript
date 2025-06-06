# Unreleased

*Currently none*

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

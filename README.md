# ya_tagscript - Yet Another TagScript fork

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/MajorTanya/ya_tagscript/test.yml?branch=v1&label=tests)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/MajorTanya/ya_tagscript/v1.svg)](https://results.pre-commit.ci/latest/github/MajorTanya/ya_tagscript/v1)
![Read the Docs (version)](https://img.shields.io/readthedocs/ya_tagscript/latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Current stable version: v1.7.0

## Information

This is a fork of PhenoM4n4n's [TagScript](https://github.com/phenom4n4n/TagScript),
which itself is a fork of JonSnowbd's
[TagScript](https://github.com/JonSnowbd/TagScript), a string templating language.

The main purpose of this fork is to align the Discord-specific blocks with the most
recent Discord and discord.py changes (new username system, etc.).

## What?

TagScript is a drop-in, easy-to-use string interpreter that lets you provide users with
ways of customizing their profiles or chat rooms with interactive text.

For example TagScript comes out of the box with a random block that would let users
provide a template that produces a new result each time its ran, or assign math and
variables for later use.

## Changes in v1

The newly released v1 includes a complete rewrite of the entire parsing and
interpretation performed by the TagScriptInterpreter class. This comes with some subtle
behavioural changes but great care was taken to keep v1 behaviourally similar to v0 and
PhenoM4n4n's fork. Most simple uses *should* behave the same but especially deeply
nested scripts or dynamically assembled ones will most likely require adjustments.
Some documentation examples were also outright wrong, so those were also adjusted to
reflect the actual behaviour of the pre-existing interpreter.

### Oh, no! Behaviour changes?!

To remove the need for dynamically assembled blocks (e.g. command blocks that only
happen under some circumstances), v1 only performs interpretation of branches that were
actually hit (to the best of its ability).

Take this (very bad) password check script:

```tagscript
{if({args}==123):{command:echo password accepted!}|something else}
```

If `{args}` is not in fact equal to `123`, the interpreter WILL NOT interpret the
command block AT ALL. It jumps straight to the `else` section after the `|` and only
interprets that. This means that for any incorrect values of `{args}`, the `echo`
command is NOT included in the list of commands in `response.actions.get("commands")`.

Other blocks with some conditional executions (like `all` or `any`) do the same.

## Installation

Download the latest version through pip:

```
pip install ya_tagscript
```

or

<!--VERSIONED TAG SECTION START-->

```
pip install git+https://github.com/MajorTanya/ya_tagscript.git@v1.7.0
```

<!--VERSIONED TAG SECTION END-->

Download from a commit:

```
pip install git+https://github.com/MajorTanya/ya_tagscript.git@<COMMIT_HASH>
```

Install for editing/development:

```
git clone https://github.com/MajorTanya/ya_tagscript.git
pip install -e ./ya_tagscript
```

## Dependencies

- `Python>=3.11`
    - before v1.4.0, this was effectively `>=3.12` due to an oversight in testing
    - after v1.4.0, Python 3.11 is _actually_ supported
- `discord.py>=2.5.0`
- `pyparsing>=3.2.0`
- `python-dateutil>=2.9.0`

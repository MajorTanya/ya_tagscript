# YATagScript - Yet Another TagScript fork

## Information

This is a fork of PhenoM4n4n's [TagScript](https://github.com/phenom4n4n/TagScript), which itself is a fork of
JonSnowbd's [TagScript](https://github.com/JonSnowbd/TagScript), a string templating language.

The main purpose of this fork is to align the Discord-specific blocks with the most recent Discord and discord.py
changes (new username system, etc.).

## Installation

Download the latest version through pip:

```
pip(3) install git+https://github.com/MajorTanya/YATagScript.git@v0.4.0
```

Download from a commit:

```
pip(3) install git+https://github.com/phenom4n4n/TagScript.git@<COMMIT_HASH>
```

Install for editing/development:

```
git clone https://github.com/phenom4n4n/TagScript.git
pip(3) install -e ./TagScript
```

## What?

TagScript is a drop in easy to use string interpreter that lets you provide users with ways of
customizing their profiles or chat rooms with interactive text.

For example TagScript comes out of the box with a random block that would let users provide
a template that produces a new result each time its ran, or assign math and variables for later
use.

## Dependencies

`Python 3.11+` (currently for ease of developing, might be extended backwards in the future) (but <=3.10 are EOL or
source-only fixes anyway)

`discord.py`

`pyparsing`

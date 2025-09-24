==========================
ya_tagscript Documentation
==========================

Yet Another TagScript fork.

The current stable release version of ya_tagscript is |version|. Check out the
:ref:`Changelog` for a change overview.

You can find the source code at the
`GitHub repository <https://github.com/MajorTanya/ya_tagscript>`_.

Project Overview
================

.. toctree::
    :maxdepth: 0

    Home <self>

.. toctree::
    :maxdepth: 1
    :caption: Getting Started

    quickstart
    intro

.. toctree::
    :maxdepth: 3
    :caption: Block Reference

    blocks

.. toctree::
    :maxdepth: 1
    :caption: API Reference

    adapters
    exceptions
    interfaces
    interpreter

.. toctree::
    :caption: Glossary

    glossary

.. toctree::
    :caption: Credits

    credits

.. toctree::
    :caption: Appendix

    changelog
    genindex
    modindex
    search
    numeric_parser

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

----

Why another fork?
=================

**TL;DR**: I was curious about basic interpreters. Then things escalated and now here
we are.

Basically just because I wanted to challenge myself to see if I could make a
lexer-parser-interpreter system work for TagScript without ever having done something
like this before. Getting to combine my favourite elements from the different
predecessors on the way was a nice bonus as well. It turned out to be quite an
undertaking but in the end, I am happy enough with the results to publish and use this
project myself.

There are some behavioural differences between this flavour of TagScript and its
predecessors but considering that every fork of the "original" `TagScript by
JonSnowbd <https://github.com/JonSnowbd/TagScript>`_ has some structural and
behavioural differences to its name, I considered them acceptable changes.

For example, `phenom4n4n's fork <https://github.com/phenom4n4n/TagScript>`_, which both
`bTagScript <https://github.com/benz206/bTagScript>`_ and this project are based on,
swapped the parameter and payload for most blocks compared to JonSnowbd's/Carl-bot's
TagScript version. This is more notable in some blocks than others.

``{require(...):...}`` from
`Carl-bot's Documentation <https://docs.carl.gg/#/tagstriggers?id=use-limiting-blocks>`_
[#carldocnote]_ makes a good example::

    # JonSnowbd/Carl-bot flavour:
    # Structure: {require(message):channel,role}
    {require(you're not cool enough):Cool kids}

This block would be transformed into the following equivalent in
phenom4n4n's fork/bTagScript/ya_tagscript::

    # phenom4n4n/bTagScript/ya_tagscript flavour:
    # Structure: {require(channel,role):message}
    {require(Cool kids):you're not cool enough}

If I hadn't forked phenom4n4n's version already, I believe I would have made this
change as well. To me, it reads more fluently as a precondition whereas the
JonSnowbd/Carl-bot flavour has forced me to double check their documentation on several
occasions. [#confusion]_

.. rubric:: Footnotes

.. [#carldocnote] Section links may not work for Carl-bot's Documentation. Check Tags &
    Triggers > Tags > Advanced Usage under section "Meta Blocks" > "Use Limiting
    Blocks" > "Require" tab.
.. [#confusion] I even messed it up while originally writing this introduction.

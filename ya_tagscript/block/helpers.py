import re
from typing import Optional

__all__ = ("implicit_bool", "helper_parse_if", "helper_split", "helper_parse_list_if")

SPLIT_REGEX = re.compile(r"(?<!\\)\|")
BOOL_LOOKUP = {"true": True, "false": False}  # potentially add more bool values


def implicit_bool(string: str) -> Optional[bool]:
    """
    Parse a string to a boolean.

    >>> implicit_bool("true")
    True
    >>> implicit_bool("FALSE")
    False
    >>> implicit_bool("abc")
    None

    Parameters
    ----------
    string: str
        The string to convert.

    Returns
    -------
    bool | None
        The boolean value of the string. None if the string failed to be parsed.
    """
    return BOOL_LOOKUP.get(string.lower())


def helper_parse_if(string: str) -> Optional[bool]:
    """
    Parse an expression string to a boolean.

    >>> helper_parse_if("this == this")
    True
    >>> helper_parse_if("2>3")
    False
    >>> helper_parse_if("40 >= 40")
    True
    >>> helper_parse_if("False")
    False
    >>> helper_parse_if("1")
    None

    Parameters
    ----------
    string: str
        The string to convert.

    Returns
    -------
    bool | None
        The boolean value of the expression. None if the expression failed to parse.
    """
    value = implicit_bool(string)
    if value is not None:
        return value
    try:
        if "!=" in string:
            spl = string.split("!=")
            return spl[0].strip() != spl[1].strip()
        if "==" in string:
            spl = string.split("==")
            return spl[0].strip() == spl[1].strip()
        if ">=" in string:
            spl = string.split(">=")
            return float(spl[0].strip()) >= float(spl[1].strip())
        if "<=" in string:
            spl = string.split("<=")
            return float(spl[0].strip()) <= float(spl[1].strip())
        if ">" in string:
            spl = string.split(">")
            return float(spl[0].strip()) > float(spl[1].strip())
        if "<" in string:
            spl = string.split("<")
            return float(spl[0].strip()) < float(spl[1].strip())
    except (IndexError, ValueError):
        pass


def helper_split(
    split_string: str,
    *,
    easy: bool = True,
    max_split: int = None,
) -> Optional[list[str]]:
    """
    A helper method to universalize the splitting logic used in multiple
    blocks and adapters. Please use this wherever a verb needs content to
    be chopped at | , or ~!

    >>> helper_split("this, should|work")
    ["this, should", "work"]
    """
    args = (max_split,) if max_split is not None else ()
    if "|" in split_string:
        return SPLIT_REGEX.split(split_string, *args)
    if easy:
        if "~" in split_string:
            return split_string.split("~", *args)
        if "," in split_string:
            return split_string.split(",", *args)
    return


def helper_parse_list_if(if_string) -> list[Optional[bool]]:
    split = helper_split(if_string, easy=False)
    if split is None:
        return [helper_parse_if(if_string)]
    return [helper_parse_if(item) for item in split]

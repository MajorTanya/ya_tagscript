import re

_PATTERN = re.compile(r"(?<!\\)([{():|}])")


def _sub_match(match: re.Match[str]) -> str:
    return "\\" + match[1]


def escape_content(string: str | None) -> str | None:
    if string is None:
        return None
    return _PATTERN.sub(_sub_match, string)

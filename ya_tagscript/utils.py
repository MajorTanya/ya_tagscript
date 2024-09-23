import re
from inspect import isawaitable
from typing import Any, Awaitable, Callable, TypeVar, Union, Optional

__all__ = ("escape_content", "maybe_await")

T = TypeVar("T")

pattern = re.compile(r"(?<!\\)([{():|}])")


def _sub_match(match: re.Match) -> str:
    return "\\" + match[1]


def escape_content(string: str) -> Optional[str]:
    """
    Escapes given input to avoid tampering with engine/block behavior.

    Returns
    -------
    str | None
        The escaped content.
    """
    if string is None:
        return
    return pattern.sub(_sub_match, string)


async def maybe_await(
    func: Callable[..., Union[T, Awaitable[T]]],
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Await the given function if it is awaitable or call it synchronously.

    Returns
    -------
    T
        The result of the awaitable function.
    """
    value = func(*args, **kwargs)
    return await value if isawaitable(value) else value

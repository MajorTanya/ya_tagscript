from collections.abc import Callable
from typing import Any

from ya_tagscript.interfaces import AdapterABC
from ya_tagscript.interpreter import Context


class FunctionAdapter(AdapterABC):
    """An adapter for a simple, no-arg function

    Caution:
        The provided function CANNOT take ANY arguments.
    """

    __slots__ = ("fn",)

    def __init__(self, function: Callable[[], Any]) -> None:
        self.fn: Callable[[], Any] = function

    def __repr__(self) -> str:
        return f"<{type(self).__qualname__} fn={self.fn!r}>"

    def get_value(self, ctx: Context) -> str | None:
        return str(self.fn())

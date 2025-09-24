from ..interfaces import AdapterABC
from ..interpreter import Context


class IntAdapter(AdapterABC):
    """An adapter for integers"""

    __slots__ = ("integer",)

    def __init__(self, integer: int) -> None:
        self.integer: int = int(integer)

    def __repr__(self) -> str:
        return f"<{type(self).__qualname__} integer={self.integer!r}>"

    def get_value(self, ctx: Context) -> str | None:
        return str(self.integer)

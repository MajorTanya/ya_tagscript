from typing import Callable, Any

from ..interface import Adapter
from ..verb import Verb


class FunctionAdapter(Adapter):
    __slots__ = ("fn",)

    def __init__(self, function_pointer: Callable[[], Any]):
        self.fn = function_pointer
        super().__init__()

    def __repr__(self) -> str:
        return f"<{type(self).__qualname__} fn={self.fn!r}>"

    def get_value(self, ctx: Verb) -> str:
        return str(self.fn())

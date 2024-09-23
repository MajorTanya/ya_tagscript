from ..interface import Adapter
from ..verb import Verb


class IntAdapter(Adapter):
    __slots__ = ("integer",)

    def __init__(self, integer: int):
        self.integer: int = int(integer)

    def __repr__(self) -> str:
        return f"<{type(self).__qualname__} integer={repr(self.integer)}>"

    def get_value(self, ctx: Verb) -> str:
        return str(self.integer)

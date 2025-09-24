from inspect import ismethod

from ..interfaces import AdapterABC
from ..interpreter import Context


class ObjectAdapter(AdapterABC):
    """An adapter for any sort of Python object

    Caution:
        The following things are unsupported and will be rejected

        - Methods
        - Private attributes (names starting with ``_``)
        - Nested attributes (``obj.a.b``)

            - ``obj.a`` is accepted
            - ``obj.a.b`` is not accepted

        - Float attributes will be truncated into integer values (``12.97 -> 12``)
    """

    __slots__ = ("obj",)

    def __init__(self, base: object) -> None:
        self.obj = base

    def __repr__(self) -> str:
        return f"<{type(self).__qualname__} object={self.obj!r}>"

    def get_value(self, ctx: Context) -> str | None:
        if ctx.node.parameter is None:
            return str(self.obj)

        parsed_param = ctx.interpret_segment(ctx.node.parameter)

        if parsed_param.startswith("_") or "." in parsed_param:
            return None

        try:
            attribute = getattr(self.obj, parsed_param)
        except AttributeError:
            return None
        if ismethod(attribute):
            return None
        elif isinstance(attribute, float):
            attribute = int(attribute)

        return str(attribute)

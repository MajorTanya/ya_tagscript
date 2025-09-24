from collections.abc import Callable
from typing import Any

from ...interfaces import AdapterABC
from ...interpreter import Context
from ...util import escape_content


class AttributeAdapter(AdapterABC):
    """A basic Discord object adapter

    **Attributes**:

    - ``id``: :class:`int` — The object's ID
    - ``created_at``: :class:`~datetime.datetime` — Represents the object's creation
      time
    - ``timestamp``: :class:`int` — The seconds-based timestamp of the object's
      ``created_at`` attribute
    - ``name``: :class:`str` — The object's name or the stringified version of the
      object if no name exists
    """

    __slots__ = ("object", "_attributes", "_methods")

    def __init__(
        self,
        base: Any,  # should be typed by each subclass, not feasible here
    ) -> None:
        self.object = base
        self._attributes = {
            "id": self.object.id,
            "created_at": self.object.created_at,
            "timestamp": int(self.object.created_at.timestamp()),
            "name": getattr(self.object, "name", str(self.object)),
        }
        self._methods: dict[str, Callable[[], Any]] = {}

    def __repr__(self) -> str:
        return f"<{type(self).__qualname__} object={self.object!r}>"

    def get_value(self, ctx: Context) -> str | None:
        should_escape = False

        return_value: str | None
        if ((param := ctx.node.parameter) is None) or (
            (parsed_param := ctx.interpret_segment(param)).strip() == ""
        ):
            return_value = str(self.object)
        else:
            try:
                value = self._attributes[parsed_param]
            except KeyError:
                if method := self._methods.get(parsed_param):
                    value = method()
                else:
                    return None

            if isinstance(value, tuple):
                value, should_escape = value

            return_value = str(value) if value is not None else None

        return escape_content(return_value) if should_escape else return_value

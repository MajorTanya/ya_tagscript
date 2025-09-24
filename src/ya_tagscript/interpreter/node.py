from __future__ import annotations

from dataclasses import dataclass
from typing import assert_never

from ..interfaces import NodeABC, NodeType


@dataclass(kw_only=True, slots=True)
class Node(NodeABC):
    """Implementation of the :class:`~ya_tagscript.interfaces.NodeABC` ABC."""

    type: NodeType
    text_value: str | None
    declaration: str | None
    parameter: str | None
    payload: str | None
    output: str | None = None

    def __repr__(self) -> str:
        return (
            f"Node(type={self.type!r}, "
            f"declaration={self.declaration!r}, "
            f"text_value={self.text_value!r}, "
            f"parameter={self.parameter!r}, "
            f"payload={self.payload!r}, "
            f"output={self.output!r}, "
            f"raw={self.as_raw_string()!r})"
        )

    def as_raw_string(self) -> str:
        match self.type:
            case NodeType.TEXT:
                return self.text_value or ""
            case NodeType.BLOCK:
                if self.declaration is None:
                    raise ValueError("Cannot have BLOCK type Node without declaration")

                if self.parameter is not None:
                    param_str = "(" + self.parameter + ")"
                else:
                    param_str = ""

                if self.payload is not None:
                    payload_str = ":" + self.payload
                else:
                    payload_str = ""

                return "{" + self.declaration + param_str + payload_str + "}"
            case _:
                assert_never(self.type)

    @classmethod
    def block(
        cls,
        *,
        declaration: str,
        parameter: str | None,
        payload: str | None,
    ) -> Node:
        return Node(
            type=NodeType.BLOCK,
            declaration=declaration,
            text_value=None,
            parameter=parameter,
            payload=payload,
        )

    @classmethod
    def text(cls, *, text_value: str) -> Node:
        return Node(
            type=NodeType.TEXT,
            text_value=text_value,
            declaration=None,
            parameter=None,
            payload=None,
        )

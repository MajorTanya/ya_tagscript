from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from enum import Enum


class NodeType(Enum):
    """Represents possible types of :class:`~ya_tagscript.interfaces.NodeABC`

    - :attr:`NodeType.BLOCK` — A (possible) TagScript block node
    - :attr:`NodeType.TEXT` — A pure text node
    """

    BLOCK = 1
    """A (possible) TagScript block node"""
    TEXT = 2
    """A pure text node"""


class NodeABC(ABC, metaclass=ABCMeta):
    """
    Represents a section of the input, either recognized as pure text or a TagScript
    block.
    """

    type: NodeType
    """
    The type of Node (either :py:enum:member:`~ya_tagscript.interfaces.NodeType.BLOCK`
    or :py:enum:member:`~ya_tagscript.interfaces.NodeType.TEXT`)
    """
    text_value: str | None
    """
    The :py:enum:member:`~ya_tagscript.interfaces.NodeType.TEXT` type node's contained
    string. Always :data:`None` for
    :py:enum:member:`~ya_tagscript.interfaces.NodeType.BLOCK` nodes.
    """
    declaration: str | None
    """
    The :py:enum:member:`~ya_tagscript.interfaces.NodeType.BLOCK` node's declaration.
    Always :data:`None` for nodes of type
    :py:enum:member:`~ya_tagscript.interfaces.NodeType.TEXT`.
    """
    parameter: str | None
    """
    The :py:enum:member:`~ya_tagscript.interfaces.NodeType.BLOCK` node's parameter.
    Always :data:`None` for nodes of type
    :py:enum:member:`~ya_tagscript.interfaces.NodeType.TEXT`.
    """
    payload: str | None
    """
    The :py:enum:member:`~ya_tagscript.interfaces.NodeType.BLOCK` node's payload.
    Always :data:`None` for nodes of type
    :py:enum:member:`~ya_tagscript.interfaces.NodeType.TEXT`.
    """
    output: str | None = None
    """
    The :py:enum:member:`~ya_tagscript.interfaces.NodeType.BLOCK` node's output once
    interpreted. :data:`None` before interpretation of the node is complete (and always
    :data:`None` for nodes of type
    :py:enum:member:`~ya_tagscript.interfaces.NodeType.TEXT`).
    """

    @abstractmethod
    def as_raw_string(self) -> str:
        """
        Returns the node's raw string representation (basically the text that this node
        was created from).

        Returns
        -------
        str
            The node's raw string representation
        """
        ...

    @classmethod
    @abstractmethod
    def block(
        cls,
        *,
        declaration: str,
        parameter: str | None,
        payload: str | None,
    ) -> NodeABC:
        """
        Convenience method to create a node of type
        :py:enum:member:`~ya_tagscript.interfaces.NodeType.BLOCK` with its exact
        required parameters.

        Parameters
        ----------
        declaration : str
            The block declaration
        parameter : str | None
            The block parameter
        payload : str | None
            The block payload

        Returns
        -------
        NodeABC
            The :class:`~ya_tagscript.interfaces.NodeABC` with a ``type`` of
            :py:enum:member:`~ya_tagscript.interfaces.NodeType.BLOCK`
        """
        ...

    @classmethod
    @abstractmethod
    def text(cls, *, text_value: str) -> NodeABC:
        """
        Convenience method to create a node of type
        :py:enum:member:`~ya_tagscript.interfaces.NodeType.TEXT` with its exact
        required parameters.

        Parameters
        ----------
        text_value : str
            The text node's string value

        Returns
        -------
        NodeABC
            The :class:`~ya_tagscript.interfaces.NodeABC` with a ``type`` of
            :py:enum:member:`~ya_tagscript.interfaces.NodeType.BLOCK`
        """
        ...

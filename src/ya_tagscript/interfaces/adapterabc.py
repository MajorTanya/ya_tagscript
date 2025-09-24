from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interpreter import Context


class AdapterABC(ABC):
    """Abstract base class for all adapter classes."""

    @abstractmethod
    def get_value(self, ctx: Context) -> str | None:
        """
        Gets the stored value based on the provided
        :class:`~ya_tagscript.interpreter.Context`

        Parameters
        ----------
        ctx : Context
            The current interpretation Context

        Returns
        -------
        str | None
            The adapter's value as a string. :data:`None` if the adapter rejected the
            context as invalid.
        """
        ...

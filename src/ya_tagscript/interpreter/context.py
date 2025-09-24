from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..interfaces import NodeABC

if TYPE_CHECKING:
    from .response import Response
    from ..interfaces import InterpreterABC


@dataclass(slots=True)
class Context:
    """An internal class used to pass the current processing state around to adapters,
    blocks, subprocessing, etc."""

    node: NodeABC
    """The node currently being processed in this Context"""
    response: Response
    """The in-progress Response"""
    interpreter: InterpreterABC
    """The interpreter instance being used to process this Context"""
    original_message: str
    """
    The raw input message as provided to the interpreter at the start of processing
    """

    def interpret_segment(self, string: str) -> str:
        """
        Runs the interpreter on the provided string. Useful for blocks to perform
        nested string interpretation.

        Parameters
        ----------
        string : str
            The string to interpret

        Returns
        -------
        str
            The fully interpreted result string
        """
        # noinspection PyProtectedMember
        return self.interpreter._interpret(
            subject=string,
            response=self.response,
            original=self.original_message,
        )

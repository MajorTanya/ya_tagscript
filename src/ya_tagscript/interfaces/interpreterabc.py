from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .adapterabc import AdapterABC
    from .blockabc import BlockABC
    from ..interpreter import Response


class InterpreterABC(ABC):

    blocks: Sequence[BlockABC]
    """The blocks being used by this interpreter instance"""
    work_limit: int | None
    """
    The approximate maximum number of characters this interpreter will process before
    aborting the processing (see also: ":term:`work limit`" in the :ref:`Glossary`)"""
    total_work: int
    """
    The total number of characters this interpreter has processed so far (This is reset
    to 0 at the beginning and end of each call to :meth:`process`)
    """

    __slots__ = ("blocks", "work_limit", "total_work")

    # noinspection PyUnusedLocal
    @abstractmethod
    def __init__(
        self,
        blocks: Sequence[BlockABC],
    ) -> None:
        """
        Constructs an interpreter with the provided block configurations

        Parameters
        ----------
        blocks : Sequence[BlockABC]
            The blocks this interpreter should use for interpretation
        """
        ...

    @abstractmethod
    def _interpret(
        self,
        subject: str,
        response: Response,
        original: str,
    ) -> str:
        """
        Private method used for actual interpretation of the ``subject`` string.

        Parameters
        ----------
        subject : str
            The string to interpret
        response : Response
            The in-progress Response. This will be modified during interpretation if
            required.
        original : str
            The raw input string originally provided to the
            :meth:`InterpreterABC.process` method.

        Returns
        -------
        str
            The interpreted output of the ``subject``.
        """
        ...

    @abstractmethod
    def process(
        self,
        input_string: str,
        seed_variables: Mapping[str, AdapterABC] | None = None,
        extra_kwargs: Mapping[str, Any] | None = None,
        work_limit: int | None = None,
    ) -> Response:
        """
        Instruct the interpreter to process the ``input_string`` with the current block
        configuration.

        Parameters
        ----------
        input_string : str
            The script to process
        seed_variables : Mapping[str, AdapterABC] | None
            A mapping of predefined variables (default: :data:`None`)
        extra_kwargs : Mapping[str, Any] | None
            A mapping of extra arguments (default: :data:`None`)
        work_limit : int | None
            The approximate character limit at which to abort processing and error out
            (default: :data:`None`)

            Note: This is only an approximate limit because a defined block may be
            short enough to still be allowed under the limit but then end up
            outputting a lot more text, shooting past the limit. The interpreter
            checks the limit after each node has been processed. This check is
            performed even during nested/recursive blocks, so one massive block with
            lots of nested blocks should still be cut off sufficiently early.

        Returns
        -------
        Response
            The output of the script as processed
        """
        ...

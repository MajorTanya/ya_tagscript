from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..interfaces import AdapterABC


class Response:
    """
    A class that bundles the textual output (:attr:`Response.body`), the defined
    actions (:attr:`Response.actions`), and variables as well as extra arguments that
    have been defined during interpretation.
    """

    __slots__ = ("body", "actions", "_variables", "extra_kwargs")

    def __init__(
        self,
        *,
        variables: Mapping[str, AdapterABC] | None,
        extra_kwargs: Mapping[str, Any] | None,
    ) -> None:
        self.body: str | None = None
        """The text output of the processed script"""
        self.actions: dict[str, Any] = {}
        """A dictionary of actions that were defined in the script"""
        self._variables: dict[str, AdapterABC] = (
            dict(variables) if variables is not None else {}
        )
        self.extra_kwargs: dict[str, Any] = (
            dict(extra_kwargs) if extra_kwargs is not None else {}
        )
        """A dictionary of extra arguments or debugging outputs"""

    def __repr__(self) -> str:
        return (
            f"<Response "
            f"body={self.body!r} "
            f"actions={self.actions!r} "
            f"variables={self.variables!r} "
            f"extra_kwargs={self.extra_kwargs!r}>"
        )

    @property
    def variables(self) -> Mapping[str, AdapterABC]:
        """A mapping of all variables defined during the script processing

        For in-progress processing, this represents all variables defined up to the
        current point in time.

        Note:
            To define/overwrite variables, use :meth:`~Response.set_variable`. This
            mapping is read-only.
        """
        return self._variables

    def set_variable(
        self,
        key: str,
        adapter: AdapterABC,
    ) -> None:
        """Stores a variable in the Response's variables mapping.

        Note:
            Due to a type variance issue, this helper method is required. Access stored
            variables through the :data:`~Response.variables` property.

        Parameters
        ----------
        key : str
            The variable's name
        adapter : AdapterABC
            The adapter holding the value that should be stored under ``key``
        """
        self._variables[key] = adapter

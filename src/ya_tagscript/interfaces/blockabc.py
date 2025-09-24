from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interpreter import Context


class BlockABC(ABC):
    """
    Abstract base class for all block types.

    All blocks must inherit from this class and implement the
    :attr:`~BlockABC._accepted_names` property and :meth:`~BlockABC.process` method.
    """

    # Note: Attributes have individual docstrings because the Sphinx output is prettier

    requires_any_parameter: bool = False
    """
    Indicates that this block requires a non-:data:`None` parameter (default:
    :data:`False`).

    Note:
        Subclasses must override this if they require this restriction.
    """
    requires_nonempty_parameter: bool = False
    """
    Indicates that this block requires a non-:data:`None` AND non-empty parameter
    (default: :data:`False`).

    When set to :data:`True`, this implies :attr:`~BlockABC.requires_any_parameter` is
    also :data:`True`.

    Note:
        Subclasses must override this if they require this restriction.
    """
    requires_any_payload: bool = False
    """
    Indicates that this block requires a non-:data:`None` payload (default:
    :data:`False`).

    Note:
        Subclasses must override this if they require this restriction.
    """
    requires_nonempty_payload: bool = False
    """
    Indicates that this block requires a non-None AND non-empty payload (default:
    :data:`False`).

    When set to :data:`True`, this implies :attr:`~BlockABC.requires_any_payload` is
    also :data:`True`.

    Note:
        Subclasses must override this if they require this restriction.
    """

    @property
    @abstractmethod
    def _accepted_names(self) -> set[str] | None:
        """
        A :class:`set` of all valid block names (all lowercase) or :data:`None` if no
        block names can be defined (e.g. variable getter blocks).

        Returns
        -------
        set[str] | None
            A set of lowercase strings representing possible acceptable block
            declarations that can be handled by this block.
            May be :data:`None` if the block does not have predefined names (e.g.
            variable getter blocks).
        """
        ...

    @abstractmethod
    def process(self, ctx: Context) -> str | None:
        """
        Execute the block's processing logic on the provided Context

        Parameters
        ----------
        ctx : Context
            The Context to process

        Returns
        -------
        str | None
            The string result of processing the Context. May be :data:`None` if the
            block has rejected the Context as invalid.
        """
        ...

    def will_accept(self, ctx: Context) -> bool:
        """
        Checks whether this block can process the provided Context

        The default check works like this:

        1. ``name_match``: Current node's :attr:`~NodeABC.declaration` is not
           :data:`None` **and** its lowercased version appears in the block's
           :attr:`~BlockABC._accepted_names` property.

        2. ``param_match``: Parameter requirements:

            a. If :attr:`~BlockABC.requires_any_parameter` is set to :data:`True`,
               check that :attr:`~NodeABC.parameter` is not :data:`None`.
            b. If :attr:`~BlockABC.requires_nonempty_parameter` is set to :data:`True`,
               check that :attr:`~NodeABC.parameter` is not :data:`None` **and** that
               :attr:`~NodeABC.parameter` is not an empty string.
            c. If neither is set, set to :data:`True` to pass the check.

        3. ``payload_match``: Payload requirements:

            a. If :attr:`~BlockABC.requires_any_payload` is set to :data:`True`, check
               that :attr:`~NodeABC.payload` is not :data:`None`.
            b. If :attr:`~BlockABC.requires_nonempty_payload` is set to :data:`True`,
               check that :attr:`~NodeABC.payload` is not :data:`None` **and** that
               :attr:`~NodeABC.payload` is not an empty string.
            c. If neither is set, set to :data:`True` to pass the check.

        4. Return ``name_match and param_match and payload_match``.

        Note:
            If a subclass requires a different check, it must override this method and
            provide its own check.

        Parameters
        ----------
        ctx : Context
            The Context for which to check if the block will accept it

        Returns
        -------
        bool
            Whether the block will accept processing of the Context
        """
        names = self._accepted_names if self._accepted_names is not None else set()
        node = ctx.node
        declaration = node.declaration

        name_match = (declaration is not None) and (declaration.lower() in names)
        param_match = True
        payload_match = True
        if self.requires_any_parameter:
            param_match = node.parameter is not None
        if self.requires_nonempty_parameter:
            param_match = (node.parameter is not None) and (node.parameter != "")
        if self.requires_any_payload:
            payload_match = node.payload is not None
        if self.requires_nonempty_payload:
            payload_match = (node.payload is not None) and (node.payload != "")
        return name_match and param_match and payload_match

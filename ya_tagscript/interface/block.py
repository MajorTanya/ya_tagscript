from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..interpreter import Context


__all__ = ("Block", "verb_required_block")


class Block:
    """
    The base class for TagScript blocks.

    Implementations must subclass this to create new blocks.

    Attributes
    ----------
    ACCEPTED_NAMES: tuple[str, ...]
        The accepted names for this block. This ideally should be set as a class
        attribute.
    """

    ACCEPTED_NAMES = ()

    def __repr__(self) -> str:
        return f"<{type(self).__qualname__} at {hex(id(self))}>"

    @classmethod
    def will_accept(cls, ctx: Context) -> bool:
        """
        Describes whether the block is valid for the given
        :class:`~ya_tagscript.interpreter.Context`.

        Parameters
        ----------
        ctx: Context
            The context object containing the :class:`~ya_tagscript.verb.Verb`.

        Returns
        -------
        bool
            Whether the block should be processed for this
            :class:`~ya_tagscript.interpreter.Context`.
        """
        dec = ctx.verb.declaration.lower()
        return dec in cls.ACCEPTED_NAMES

    def pre_process(self, _ctx: Context):
        return None

    def process(self, ctx: Context) -> Optional[str]:
        """
        Processes the block's actions for a given
        :class:`~ya_tagscript.interpreter.Context`.

        Subclasses must implement this.

        Parameters
        ----------
        ctx: Context
            The context object containing the :class:`~ya_tagscript.verb.Verb`.

        Returns
        -------
        str | None
            The block's processed value.

        Raises
        ------
        NotImplementedError
            The subclass did not implement this required method.
        """
        raise NotImplementedError

    def post_process(self, _ctx: Context):
        return None


@lru_cache(maxsize=None)
def verb_required_block(
    implicit: bool,
    *,
    parameter: bool = False,
    payload: bool = False,
) -> type[Block]:
    """
    Get a Block subclass that requires a verb to implicitly or explicitly have a
    parameter or payload passed.

    Parameters
    ----------
    implicit: bool
        Specifies whether the value is required to be passed implicitly or explicitly.
        ``{block()}`` would be allowed if implicit is False.
    parameter: bool
        Passing True will cause the block to require a parameter to be passed.
    payload: bool
        Passing True will cause the block to require the payload to be passed.
    """
    check = (lambda x: x) if implicit else (lambda x: x is not None)

    class RequireMeta(type):
        def __repr__(self) -> str:
            return f"VerbRequiredBlock(implicit={implicit!r}, payload={payload!r}, parameter={parameter!r})"

    class VerbRequiredBlock(Block, metaclass=RequireMeta):
        def will_accept(self, ctx: Context) -> bool:
            verb = ctx.verb
            if payload and not check(verb.payload):
                return False
            if parameter and not check(verb.parameter):
                return False
            return super().will_accept(ctx)

    return VerbRequiredBlock

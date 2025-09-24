from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext.commands import Cooldown

from ..interfaces import InterpreterABC

if TYPE_CHECKING:
    from ..interpreter import Response


class TagScriptError(Exception):
    """Base class for all module errors."""

    pass


class WorkloadExceededError(TagScriptError):
    """Raised when the interpreter goes over the provided character limit."""

    pass


class ProcessError(TagScriptError):
    """
    Raised when an exception occurs during interpreter processing.

    Attributes
    ----------
    original: Exception
        The original exception that occurred during processing.
    response: Response
        The incomplete response that was being processed when the exception occurred.
    interpreter: InterpreterABC
        The interpreter used for processing.
    """

    def __init__(
        self,
        error: Exception,
        response: Response,
        interpreter: InterpreterABC,
    ) -> None:
        self.original: Exception = error
        self.response: Response = response
        self.interpreter: InterpreterABC = interpreter
        super().__init__(error)


class EmbedParseError(TagScriptError):
    """Raised if an exception occurs while attempting to parse an embed."""

    pass


class BadColourArgument(EmbedParseError):
    """
    Raised when the passed input fails to convert to `discord.Colour`.

    Attributes
    ----------
    argument: str
        The invalid input.
    """

    def __init__(self, argument: str) -> None:
        self.argument = argument
        super().__init__(f'Colour "{argument}" is invalid.')


class StopError(TagScriptError):
    """
    Raised by the StopBlock to stop processing.

    Attributes
    ----------
    message: str
        The stop error message.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class CooldownExceeded(StopError):
    """
    Raised by the cooldown block when a cooldown is exceeded.

    Attributes
    ----------
    message: str
        The cooldown error message.
    cooldown: discord.app_commands.Cooldown
        The cooldown bucket with information on the cooldown.
    key: str
        The cooldown key that reached its cooldown.
    retry_after: float
        The seconds left til the cooldown ends.
    """

    def __init__(
        self,
        message: str,
        cooldown: Cooldown,
        key: str,
        retry_after: float,
    ) -> None:
        self.cooldown = cooldown
        self.key = key
        self.retry_after = retry_after
        super().__init__(message)

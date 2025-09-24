import logging
from collections.abc import Mapping, Sequence
from typing import Any, assert_never

from .context import Context
from .node import Node
from .response import Response
from .ts_parser import TagScriptParser
from ..exceptions import ProcessError, StopError, TagScriptError, WorkloadExceededError
from ..interfaces import (
    AdapterABC,
    BlockABC,
    InterpreterABC,
    NodeABC,
    NodeType,
)

_logger = logging.getLogger(__name__)


class TagScriptInterpreter(InterpreterABC):

    __slots__ = ("blocks", "_parser", "work_limit", "total_work")

    def __init__(
        self,
        blocks: Sequence[BlockABC],
    ) -> None:
        self._parser = TagScriptParser()
        self.blocks: Sequence[BlockABC] = blocks
        self.work_limit: int | None = None
        self.total_work: int = 0

    def process(
        self,
        input_string: str,
        seed_variables: Mapping[str, AdapterABC] | None = None,
        extra_kwargs: Mapping[str, Any] | None = None,
        work_limit: int | None = None,
    ) -> Response:
        self.work_limit = work_limit
        response = Response(variables=seed_variables, extra_kwargs=extra_kwargs)
        try:
            output = self._interpret(
                subject=input_string,
                response=response,
                original=input_string,
            )
        except TagScriptError:
            raise
        except Exception as e:
            raise ProcessError(e, response, self) from e

        # one last pass, particularly to catch dynamically assembled blocks
        if response.body is None:
            response.body = self._interpret(output, response, input_string).strip()
        else:
            response.body = self._interpret(
                response.body,
                response,
                input_string,
            ).strip()
        self.total_work = 0
        return response

    def _interpret(
        self,
        subject: str,
        response: Response,
        original: str,
    ) -> str:
        if subject == "":
            return ""
        elif not ("{" in subject) or not ("}" in subject):
            # to interpret anything, we need blocks
            # ALL blocks MUST be enclosed in a pair of braces (basic block anatomy)
            # if we don't have even one of each brace, this is uninterpretable
            # in other words, this is plaintext to us
            return subject
        ast = self._parser.parse(subject)
        output: list[str] = []
        node_processing_fn = self._process_node
        for node in ast:
            try:
                node_output = node_processing_fn(node, response, original)
                output.append(node_output)
            except StopError as e:
                _logger.debug("StopError raised on %r", node, exc_info=e)
                output = [e.message]
                break

            if node.type != NodeType.TEXT:
                # don't consider pure text as "work" in relation to the limit
                self.total_work = _check_workload(
                    self.work_limit,
                    self.total_work,
                    node_output,
                )

        return "".join(output)

    def _process_context(self, ctx: Context) -> str | None:
        for b in self.blocks:
            if b.will_accept(ctx):
                processed = b.process(ctx)
                if processed is not None:
                    result = str(processed)
                    ctx.node.output = result
                    return result
        return None

    def _process_node(
        self,
        node: NodeABC,
        response: Response,
        original_subject: str,
    ) -> str:
        if node.type == NodeType.TEXT:
            _logger.debug("Processing text node %r", node)
            return node.text_value or ""
        elif node.type == NodeType.BLOCK:
            ctx = Context(node, response, self, original_subject)
            _logger.debug("Processing block node with context %r", ctx)

            output = self._process_context(ctx)

            if output is not None:
                return output
            else:
                return self._resolve_block_rejection(ctx, node)
        else:
            assert_never(node.type)

    def _resolve_block_rejection(self, ctx: Context, node: NodeABC) -> str:
        if node.type != NodeType.BLOCK:
            return ""

        response = ctx.response
        original_message = ctx.original_message

        while True:
            interpreted_declaration = self._interpret(
                (node.declaration or ""),
                response,
                original_message,
            )

            if interpreted_declaration == node.declaration:
                # declaration fully rejected, attempt parameter and payload each
                # these may have interpretable data to output
                # (maybe typo in the declaration)
                if node.parameter is None:
                    param = None
                else:
                    param = self._interpret(
                        subject=(node.parameter or ""),
                        response=response,
                        original=original_message,
                    )

                if node.payload is None:
                    payload = None
                else:
                    payload = self._interpret(
                        subject=(node.payload or ""),
                        response=response,
                        original=original_message,
                    )

                if param != node.parameter or payload != node.payload:
                    node.parameter = param
                    node.payload = payload
                return node.as_raw_string()
            else:
                # success! something changed, attempt full node processing
                node = Node.block(
                    declaration=interpreted_declaration,
                    parameter=node.parameter,
                    payload=node.payload,
                )
                ctx.node = node
                partial_out = self._process_context(ctx)
                if partial_out is not None:
                    return partial_out
                # else: loop to top of while True and attempt processing again


def _check_workload(work_limit: int | None, total_work: int, output: str) -> int:
    # this is never going to hit at the limit exactly, but should prevent infinite work
    total_work += len(output)
    if work_limit is not None and total_work > work_limit:
        raise WorkloadExceededError(
            (
                f"The Tagscript interpreter has surpassed the workload limit. "
                f"Processed {total_work}/{work_limit}.",
            ),
        )
    return total_work

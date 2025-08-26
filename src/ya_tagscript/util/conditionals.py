import logging
from typing import NamedTuple

from ..interpreter import Context

_log = logging.getLogger(__name__)


class OperatorLocation(NamedTuple):
    operator: str | None
    start_idx: int
    end_idx: int


def parse_condition(ctx: Context, condition: str) -> bool | None:
    if (found_op := _find_zero_depth_operator(condition)) is None:
        parsed_condition = ctx.interpret_segment(condition)
        if parsed_condition.lower() == "true":  # constant conditions
            return True
        elif parsed_condition.lower() == "false":  # constant conditions
            return False
        return None

    left_cond, right_cond = (
        condition[: found_op.start_idx],
        condition[found_op.end_idx :],
    )
    _log.debug(
        f"Requested expression: %r %r %r",
        left_cond,
        found_op,
        right_cond,
    )

    left_parsed = ctx.interpret_segment(left_cond)
    right_parsed = ctx.interpret_segment(right_cond)

    condition_fulfilled = _execute_operator(
        left_parsed,
        found_op.operator,
        right_parsed,
    )

    return condition_fulfilled


def _find_zero_depth_operator(string: str) -> OperatorLocation | None:
    """Find the first operator (==, !=, >=, <=, >, <) at zero nesting depth."""
    operators = ["==", "!=", ">=", "<=", ">", "<"]
    depth = 0

    for i, ch in enumerate(string):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif depth == 0:
            if i + 1 < len(string):
                possible_op = string[i : i + 2]
                if possible_op in operators:
                    return OperatorLocation(possible_op, i, i + len(possible_op))
            possible_op = ch
            if possible_op in operators:
                return OperatorLocation(possible_op, i, i + len(possible_op))

    return None


def _execute_operator(left: str, operator: str | None, right: str) -> bool | None:
    """Executes the boolean operator specified"""
    match operator:
        case "==":
            return left == right
        case "!=":
            return left != right
        case "<=":
            return float(left) <= float(right)
        case ">=":
            return float(left) >= float(right)
        case "<":
            return float(left) < float(right)
        case ">":
            return float(left) > float(right)
        case _:
            return None

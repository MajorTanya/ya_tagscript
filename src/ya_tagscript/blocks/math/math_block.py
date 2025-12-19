import logging
import math
import operator
from collections.abc import Callable
from typing import Any

from pyparsing import (
    CaselessKeyword,
    DelimitedList,
    Forward,
    Group,
    Literal,
    ParseResults,
    Regex,
    Suppress,
    Word,
    alphanums,
    alphas,
)
from pyparsing.exceptions import ParseBaseException

from ...interfaces import BlockABC
from ...interpreter import Context

E_STR = "E"
PI_STR = "PI"
PI_STR_LETTER = "π"
TAU_STR = "TAU"
TAU_STR_LETTER = "τ"
UNARY_MINUS = "unary -"

_log = logging.getLogger(__name__)


class NumericStringParser:
    """
    This is the grammar used by this class:

    The ``consts`` values are all caseless, so ``pi``, ``PI``, etc., all work.

        .. productionlist::
            consts    : E | PI | π | TAU | τ
            float_num : [+-]?\\d+(?:\\.\\d*)?(?:[eE][+-]?\\d+)?
            ident     : [a-zA-Z][a-zA-Z0-9_$]*
            addop     : '+' | '-'
            multop    : '*' | '/' | '%'
            iop       : '+=' | '-=' | '*=' | '/='
            expop     : '^'
            atom      : consts | float_num | ident | fn_call | '(' expr ')'
            factor    : atom [ expop factor ]*
            term      : factor [ multop factor ]*
            expr      : term [ addop term ]*
            expr_list : expr (',' expr)*
            fn_call   : ident '(' expr_list ')'
            final     : expr [ iop expr ]*
    """

    # Most of this code comes from the fourFn.py pyparsing example
    # cf. https://github.com/pyparsing/pyparsing/blob/e1a69f12e2e9913997feb5390652762e71d47523/examples/fourFn.py

    EPSILON: float = 1e-12
    """Maximum precision used by the parser"""

    # map operator symbols to corresponding arithmetic operations
    _operations: dict[str, Callable[[int | float, int | float], int | float]] = {
        "+": operator.add,
        "-": operator.sub,
        "+=": operator.iadd,
        "-=": operator.isub,
        "*": operator.mul,
        "*=": operator.imul,
        "/": operator.truediv,
        "/=": operator.itruediv,
        "^": operator.pow,
        "%": operator.mod,
    }

    # map function names to corresponding math functions
    # Any arg because functions take different types and numbers of arguments
    _functions: dict[str, Callable[[Any], int | float]] = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "exp": math.exp,
        "abs": abs,
        "trunc": lambda a: int(a),
        "round": round,
        "sgn": (
            lambda a: abs(a) > NumericStringParser.EPSILON and ((a > 0) - (a < 0)) or 0
        ),
        "log": math.log10,
        "ln": math.log,
        "log2": math.log2,
        "sqrt": math.sqrt,
        "hypot": math.hypot,
    }

    def _insert_fn_arg_count_tuple(self, tokens: ParseResults) -> None:
        fn = tokens.pop(0)
        num_args = len(tokens[0])
        tokens.insert(0, (fn, num_args))

    def _push_first(self, tokens: ParseResults) -> None:
        self.expression_stack.append(tokens[0])  # type: ignore

    def _push_unary_minus(self, tokens: ParseResults) -> None:
        if tokens[0] == "-":
            self.expression_stack.append(UNARY_MINUS)

    def __init__(self) -> None:
        self.expression_stack: list[str | tuple[str, int]] = []
        # use CaselessKeyword for e and pi, to avoid accidentally matching
        # functions that start with 'e' or 'pi' (such as 'exp'); Keyword
        # and CaselessKeyword only match whole words
        e = CaselessKeyword(E_STR)
        pi = CaselessKeyword(PI_STR) | CaselessKeyword(PI_STR_LETTER)
        tau = CaselessKeyword(TAU_STR) | CaselessKeyword(TAU_STR_LETTER)
        consts = e | pi | tau

        float_num = Regex(r"[+-]?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?")
        ident = Word(alphas, alphanums + "_$")

        plus, minus, mult, div, mod = map(Literal, "+-*/%")
        lpar, rpar = map(Suppress, "()")

        iadd, imult, idiv, isub = map(Literal, ["+=", "*=", "/=", "-="])

        addop = plus | minus
        multop = mult | div | mod
        iop = iadd | isub | imult | idiv
        expop = Literal("^")

        expr = Forward()
        expr_list = DelimitedList(Group(expr))

        fn_call = (ident + lpar - Group(expr_list) + rpar).set_parse_action(
            self._insert_fn_arg_count_tuple,
        )

        atom = (
            addop[...]
            + (
                (consts | fn_call | float_num | ident).set_parse_action(
                    self._push_first,
                )
                | Group(lpar + expr + rpar)
            )
        ).set_parse_action(self._push_unary_minus)

        # by defining exponentiation as "atom [ ^ factor ]..." instead of
        # "atom [ ^ atom ]...", we get right-to-left exponents, instead of
        # left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = Forward()

        factor <<= atom + (expop + factor).set_parse_action(self._push_first)[...]
        term = factor + (multop + factor).set_parse_action(self._push_first)[...]
        expr <<= term + (addop + term).set_parse_action(self._push_first)[...]
        final = expr + (iop + expr).set_parse_action(self._push_first)[...]

        self.parser = final

    def _evaluate_stack(self, stack: list[str | tuple[str, int]]) -> int | float:
        # string value OR tuple[fn name str, num_args int]
        op, num_args = stack.pop(), 0
        if isinstance(op, tuple):
            op, num_args = op

        if op in self._operations:
            op2 = self._evaluate_stack(stack)
            op1 = self._evaluate_stack(stack)
            return self._operations[op](op1, op2)
        # be case-insensitive about function names
        elif op.lower() in self._functions:
            lowered = op.lower()
            args = list(
                reversed([self._evaluate_stack(stack) for _ in range(num_args)]),
            )
            if lowered == "round" and num_args == 2:
                # round needs the second arg to be int
                args[1] = int(args[1])
            return self._functions[lowered](*args)
        elif op == UNARY_MINUS:
            return -self._evaluate_stack(stack)
        elif op == PI_STR or op == PI_STR_LETTER:
            return math.pi  # 3.141592653589793
        elif op == E_STR:
            return math.e  # 2.718281828459045
        elif op in {TAU_STR, TAU_STR_LETTER}:
            return math.tau  # 6.283185307179586
        else:
            if op[0].isalpha():
                raise ValueError(f"Invalid identifier {op!r}")
            return float(op)

    def eval(self, num_string: str, parse_all: bool = True) -> int | float:
        """
        Evaluates the ``num_string`` mathematical expression

        Parameters
        ----------
        num_string : str
            The mathematical expression string to parse and evaluate
        parse_all : bool
            Whether the entire string has to match the grammar (default: :data:`True`)

        Returns
        -------
        int | float
            The calculated result

        Raises
        ------
        :exc:`pyparsing.ParseException`
            Raised if ``parse_all`` is :data:`True` but ``num_string`` did not fully
            match the grammar
        ValueError
            Raised if an invalid identifier is used that is not a supported constant,
            operator, or function
        """
        self.expression_stack = []
        # parse_string side effect is filling the expression stack we evaluate later
        self.parser.parse_string(num_string, parse_all)
        result = self._evaluate_stack(self.expression_stack[:])
        if isinstance(result, float):
            return round(result, 15)
        else:
            return result


class MathBlock(BlockABC):
    """
    This block evaluates mathematical expressions provided in the payload.

    All supported constants and functions are listed below.

    The output is always rounded to 15 decimal places, unless one of the decimal-free
    methods mentioned below is used, in which case no decimal places are returned.

    For most operations and functions, if a whole number is returned, the number will
    still carry a ``.0`` with it (e.g. ``1+2`` = ``3.0``). The only functions which
    will *never* output trailing decimals like that are:

    - ``sgn`` — (only returns ``-1`` for negative numbers, ``0`` for zero, or ``1`` for
      positive numbers)
    - ``trunc(a)`` — (Truncates a by throwing away all decimal places, e.g. ``4.999``
      -> ``4``)
    - ``round(a)`` — (with no precision argument, ``a`` is rounded to the nearest
      integer, so ``4.7`` -> ``5``)

    Note:
        ``round(a, n)`` will always return decimal places, including ``.0`` for
        precision 0, i.e. ``round(4, 0)`` -> ``4.0``)

    **Usage**: ``{math:<payload>}``

    **Aliases**: ``math``, ``m``, ``+``, ``calc``

    **Parameter**: ``None``

    **Payload**: ``payload`` (required)

    **Examples**::

        {math:1 + 2 * 3}
        # 7.0
        {math:PI * 2}
        # 6.283185307179586
        {math:round(10 / 3, 2)}
        # 3.33

    **Supported Mathematical Expressions**:

    +-------------------------+----------------------------------------------+-------------------+
    | Expression              | Description                                  | Notes             |
    +=========================+==============================================+===================+
    | ``a + b``               | Addition                                     |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``a - b``               | Subtraction                                  |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``a * b``               | Multiplication                               |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``a / b``               | Division                                     |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``a % b``               | Modulo operation (remainder of ``a / b``)    |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``a ^ b``               | Exponentiation (``a`` to the power of ``b``) |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``sin(a)``              | Sine function                                |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``sinh(a)``             | Hyperbolic sine function                     |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``cos(a)``              | Cosine function                              |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``cosh(a)``             | Hyperbolic Cosine function                   |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``tan(a)``              | Tangens function                             |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``tanh(a)``             | Hyperbolic Tangens function                  |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``exp(a)``              | Exponential function (``e^a``)               |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``ln(a)``               | Natural logarithm function (log base e)      |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``log(a)``              | Logarithmic function (log base 10)           |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``log2(a)``             | Logarithmic function (log base 2)            |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``sqrt(a)``             | Square root of ``a``                         |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``hypot(a,b)``          | Hypotenuse of a right triangle with sides    |                   |
    |                         | ``a`` and ``b``                              |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``abs(a)``              | Absolute value of ``a``                      |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``sgn(a)``              | Signum function: ``-1`` if ``a<0``,          | no decimals       |
    |                         | ``0`` if ``a==0``, ``1`` if ``a>0``          | (-1 or 0 or 1)    |
    +-------------------------+----------------------------------------------+-------------------+
    | ``round(a)``            | Rounds ``a`` to the nearest integer          | no decimals       |
    +-------------------------+----------------------------------------------+-------------------+
    | ``round(a,n)``          | Rounds ``a`` to ``n`` decimal places         |                   |
    +-------------------------+----------------------------------------------+-------------------+
    | ``trunc(a)``            | Truncates ``a`` to its integer part          | no decimals       |
    +-------------------------+----------------------------------------------+-------------------+
    | ``E``, ``e``            | Euler's number, rounded to 15 decimal places | 2.718281828459045 |
    +-------------------------+----------------------------------------------+-------------------+
    | ``PI``, ``pi``, ``π``   | Pi, rounded to 15 decimal places             | 3.141592653589793 |
    +-------------------------+----------------------------------------------+-------------------+
    | ``TAU``, ``tau``, ``τ`` | Tau, rounded to 15 decimal places            | 6.283185307179586 |
    +-------------------------+----------------------------------------------+-------------------+

    If you're curious, here is :ref:`the Numeric String Parser`.
    """

    _NSP = NumericStringParser()
    requires_nonempty_payload = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"math", "m", "+", "calc"}

    def process(self, ctx: Context) -> str | None:
        if (payload := ctx.node.payload) is None or payload.strip() == "":
            return None

        parsed_payload = ctx.interpret_segment(payload)
        try:
            return str(self._NSP.eval(parsed_payload))
        except (
            ValueError,
            OverflowError,
            ZeroDivisionError,
            ParseBaseException,
        ) as e:
            _log.debug(e)
            return None

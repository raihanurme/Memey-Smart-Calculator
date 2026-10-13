import ast
import math
import operator
import re
from decimal import Decimal, DivisionByZero, InvalidOperation, localcontext

from app.core.functions import CalculationError, scientific_function
from app.core.smart import normalize_expression


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCTION_NAMES = {"sin", "cos", "tan", "log", "ln", "sqrt"}
_MAX_INPUT_LENGTH = 512
_MAX_AST_NODES = 128
_MAX_POWER = Decimal(1000)
_MAX_ADJUSTED_EXPONENT = 1000


class Calculator:
    def __init__(self):
        self.ans = Decimal(0)
        self.angle_mode = "DEG"

    def evaluate(self, expression):
        if not isinstance(expression, str) or not expression.strip():
            raise CalculationError("Masukkan ekspresi terlebih dahulu")
        if len(expression) > _MAX_INPUT_LENGTH:
            raise CalculationError("Ekspresi terlalu panjang")

        normalized = normalize_expression(expression)
        normalized = re.sub(r"(?<![A-Za-z0-9_])π(?![A-Za-z0-9_])", "pi", normalized)
        normalized = re.sub(r"(?<![A-Za-z0-9_])√", "sqrt", normalized)
        try:
            tree = ast.parse(normalized, mode="eval")
        except (SyntaxError, ValueError) as error:
            raise CalculationError("Ekspresi tidak valid") from error
        if sum(1 for _ in ast.walk(tree)) > _MAX_AST_NODES:
            raise CalculationError("Ekspresi terlalu kompleks")

        try:
            with localcontext() as context:
                context.prec = 28
                result = self._evaluate_node(tree.body)
        except CalculationError:
            raise
        except (DivisionByZero, ZeroDivisionError):
            raise CalculationError("Tidak bisa dibagi nol")
        except (InvalidOperation, OverflowError, ArithmeticError, ValueError):
            raise CalculationError("Hasil tidak dapat dihitung")
        if not result.is_finite() or abs(result.adjusted()) > _MAX_ADJUSTED_EXPONENT:
            raise CalculationError("Hasil terlalu besar")
        return result

    def _evaluate_node(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise CalculationError("Ekspresi tidak valid")
            return Decimal(str(node.value))
        if isinstance(node, ast.Num):
            return Decimal(str(node.n))
        if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
            left = self._evaluate_node(node.left)
            right = self._evaluate_node(node.right)
            if isinstance(node.op, ast.Pow):
                if abs(right) > _MAX_POWER:
                    raise CalculationError("Pangkat terlalu besar")
                if left == 0 and right < 0:
                    raise CalculationError("Tidak bisa dibagi nol")
                if right != right.to_integral_value() and left < 0:
                    raise CalculationError("Pangkat pecahan untuk angka negatif tidak tersedia")
            result = _BINARY_OPERATORS[type(node.op)](left, right)
            if not result.is_finite() or (
                result != 0 and abs(result.adjusted()) > _MAX_ADJUSTED_EXPONENT
            ):
                raise CalculationError("Hasil terlalu besar")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
            return _UNARY_OPERATORS[type(node.op)](self._evaluate_node(node.operand))
        if isinstance(node, ast.Name):
            if node.id == "pi":
                return Decimal("3.141592653589793238462643383")
            if node.id == "e":
                return Decimal("2.718281828459045235360287471")
            if node.id == "ans":
                return self.ans
            raise CalculationError("Ekspresi tidak valid")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name == "factorial":
                if len(node.args) != 1 or node.keywords:
                    raise CalculationError("Ekspresi tidak valid")
                value = self._evaluate_node(node.args[0])
                if value != value.to_integral_value() or value < 0 or value > 500:
                    raise CalculationError("Faktorial memerlukan bilangan bulat 0–500")
                return Decimal(math.factorial(int(value)))
            if name not in _FUNCTION_NAMES or len(node.args) != 1 or node.keywords:
                raise CalculationError("Ekspresi tidak valid")
            return scientific_function(
                name, self._evaluate_node(node.args[0]), self.angle_mode
            )
        raise CalculationError("Ekspresi tidak valid")

    def calculate(self, expression):
        result = self.evaluate(expression)
        self.ans = result
        return result


def format_decimal(value):
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in ("", "-0"):
        text = "0"
    integer, separator, fraction = text.partition(".")
    sign = ""
    if integer.startswith("-"):
        sign, integer = "-", integer[1:]
    integer = "{:,}".format(int(integer or "0"))
    return sign + integer + (separator + fraction if separator else "")

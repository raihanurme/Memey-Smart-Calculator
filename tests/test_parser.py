from decimal import Decimal

import pytest

from app.core.functions import CalculationError
from app.core.parser import Calculator, format_decimal


@pytest.fixture
def calculator():
    return Calculator()


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("2+3*4", "14"),
        ("(2+3)*4", "20"),
        ("10/4", "2.5"),
        ("0.1+0.2", "0.3"),
        ("20% dari 500", "100"),
        ("500+10%", "550"),
        ("500-15%", "425"),
        ("10%3", "1"),
        ("2^10", "1,024"),
        ("√144", "12"),
        ("sin(30)", "0.5"),
        ("1,5+0,5", "2"),
        ("5!", "120"),
    ],
)
def test_calculation_examples(calculator, expression, expected):
    assert format_decimal(calculator.evaluate(expression)) == expected


def test_degrees_and_radians(calculator):
    assert calculator.evaluate("sin(30)") == Decimal("0.5")
    calculator.angle_mode = "RAD"
    assert calculator.evaluate("sin(pi/2)") == Decimal("1")


def test_ans_is_previous_successful_result(calculator):
    calculator.calculate("12+8*3")
    assert calculator.evaluate("ans/2") == Decimal("18")
    with pytest.raises(CalculationError):
        calculator.calculate("1/0")
    assert calculator.ans == Decimal("36")


@pytest.mark.parametrize(
    "expression, message",
    [
        ("5/0", "Tidak bisa dibagi nol"),
        ("2+*3", "Ekspresi tidak valid"),
        ("__import__('os')", "Ekspresi tidak valid"),
        ("open('secret')", "Ekspresi tidak valid"),
        ("sqrt(-1)", "Akar bilangan negatif"),
    ],
)
def test_invalid_or_unsafe_input_is_rejected(calculator, expression, message):
    with pytest.raises(CalculationError, match=message):
        calculator.evaluate(expression)


def test_expression_size_and_result_are_bounded(calculator):
    with pytest.raises(CalculationError, match="terlalu panjang"):
        calculator.evaluate("1" * 513)
    with pytest.raises(CalculationError, match="Pangkat terlalu besar"):
        calculator.evaluate("2^1001")


def test_number_formatting_groups_thousands():
    assert format_decimal(Decimal("1234567.5000")) == "1,234,567.5"

import math
from decimal import Decimal, InvalidOperation


class CalculationError(ValueError):
    """An input or calculation error that is safe to show to the user."""


def scientific_function(name, value, angle_mode):
    try:
        if name == "sqrt":
            if value < 0:
                raise CalculationError("Akar bilangan negatif tidak tersedia")
            return value.sqrt()
        if name == "ln":
            if value <= 0:
                raise CalculationError("Logaritma hanya untuk angka positif")
            return value.ln()
        if name == "log":
            if value <= 0:
                raise CalculationError("Logaritma hanya untuk angka positif")
            return value.log10()
        if name in ("sin", "cos", "tan"):
            argument = float(value)
            if angle_mode == "DEG":
                argument = math.radians(argument)
            result = getattr(math, name)(argument)
            if not math.isfinite(result):
                raise CalculationError("Hasil fungsi tidak terdefinisi")
            return Decimal(format(result, ".15g"))
    except CalculationError:
        raise
    except (InvalidOperation, OverflowError, ValueError) as error:
        raise CalculationError("Hasil fungsi tidak terdefinisi") from error
    raise CalculationError("Fungsi tidak dikenal")

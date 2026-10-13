"""Small, dependency-free unit conversion helpers."""

_LENGTH_TO_METERS = {
    "mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0,
    "in": 0.0254, "ft": 0.3048, "mi": 1609.344,
}
_MASS_TO_GRAMS = {
    "mg": 0.001, "g": 1.0, "kg": 1000.0, "lb": 453.59237, "oz": 28.349523125,
}
_VOLUME_TO_LITERS = {
    "ml": 0.001, "l": 1.0, "m3": 1000.0, "cup": 0.2365882365,
}


def convert(value, source, target, category):
    value = float(value)
    units = {
        "length": _LENGTH_TO_METERS,
        "mass": _MASS_TO_GRAMS,
        "volume": _VOLUME_TO_LITERS,
    }
    if category == "temperature":
        to_celsius = {
            "c": lambda number: number,
            "f": lambda number: (number - 32) * 5 / 9,
            "k": lambda number: number - 273.15,
        }
        from_celsius = {
            "c": lambda number: number,
            "f": lambda number: number * 9 / 5 + 32,
            "k": lambda number: number + 273.15,
        }
        if source not in to_celsius or target not in from_celsius:
            raise ValueError("Unit suhu tidak dikenal")
        return from_celsius[target](to_celsius[source](value))
    if category not in units or source not in units[category] or target not in units[category]:
        raise ValueError("Kategori atau unit tidak dikenal")
    return value * units[category][source] / units[category][target]

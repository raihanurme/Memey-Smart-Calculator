import re


_PERCENT_OF = re.compile(
    r"(?i)(\d+(?:[.,]\d+)?)\s*%\s*dari\s*(\d+(?:[.,]\d+)?)"
)
_ADD_SUB_PERCENT = re.compile(
    r"(?P<base>\([^()]*\)|\d+(?:[.,]\d+)?)\s*"
    r"(?P<operator>[+-])\s*(?P<percent>\d+(?:[.,]\d+)?)\s*%"
)
_ROOT_ARGUMENT = re.compile(r"√\s*(\([^()]*\)|\d+(?:[.,]\d+)?)")
_FACTORIAL_ARGUMENT = re.compile(r"(\([^()]*\)|\d+(?:[.,]\d+)?)\s*!")
_NUMBER_COMMA = re.compile(r"(?<=\d),(?=\d)")


def normalize_expression(expression):
    text = expression.strip()
    text = text.replace("×", "*").replace("÷", "/").replace("−", "-")
    text = text.replace("^", "**").replace("²", "**2")
    text = _PERCENT_OF.sub(r"((\1)/100*(\2))", text)

    def percentage_change(match):
        base = match.group("base")
        operator = match.group("operator")
        percentage = match.group("percent")
        return "({base}{op}({base}*{pct}/100))".format(
            base=base, op=operator, pct=percentage
        )

    text = _ADD_SUB_PERCENT.sub(percentage_change, text)
    text = _ROOT_ARGUMENT.sub(r"sqrt(\1)", text)
    text = _FACTORIAL_ARGUMENT.sub(r"factorial(\1)", text)
    text = _NUMBER_COMMA.sub(".", text)
    text = re.sub(
        r"(\d+(?:\.\d+)?)\s*%(?!\s*(?:\d|[A-Za-z_(]))",
        r"(\1/100)",
        text,
    )
    return text

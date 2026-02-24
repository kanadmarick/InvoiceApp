from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django import template

register = template.Library()


def _group_indian_number(value_str):
    if len(value_str) <= 3:
        return value_str

    last_three = value_str[-3:]
    rest = value_str[:-3]
    parts = []

    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]

    if rest:
        parts.insert(0, rest)

    return ",".join(parts + [last_three])


@register.filter
def rupee(value):
    try:
        amount = Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError):
        return value

    sign = "-" if amount < 0 else ""
    amount = abs(amount)

    amount_str = f"{amount:.2f}"
    int_part, dec_part = amount_str.split(".")
    grouped = _group_indian_number(int_part)

    if dec_part == "00":
        return f"{sign}₹ {grouped}"

    return f"{sign}₹ {grouped}.{dec_part}"

"""
Tiny helpers for price explainers (formatting, ranges, hours-to-afford).
"""
from __future__ import annotations
from decimal import Decimal, InvalidOperation

__all__ = ["format_price", "midpoint", "hours_to_afford"]

def _to_decimal(x) -> Decimal:
    try:
        return x if isinstance(x, Decimal) else Decimal(str(x))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"Value '{x}' cannot be converted to Decimal")

def format_price(value, currency: str = "$", per: str | None = None, precision: int = 2) -> str:
    """
    Format a numeric price with currency symbol and optional 'per' unit.
    >>> format_price(12.5, "$", "lb")
    '$12.50 per lb'
    """
    d = _to_decimal(value).quantize(Decimal(10) ** -precision)
    out = f"{currency}{d}"
    if per:
        out += f" per {per}"
    return out

def midpoint(low, high, precision: int = 2):
    """
    Midpoint of two numbers.
    >>> midpoint(9, 11)
    Decimal('10.00')
    """
    dlow = _to_decimal(low)
    dhigh = _to_decimal(high)
    mid = (dlow + dhigh) / 2
    return mid.quantize(Decimal(10) ** -precision)

def hours_to_afford(price, hourly_wage, precision: int = 2):
    """
    Convert a price into hours of work at a given wage.
    >>> hours_to_afford(28.5, 15)
    Decimal('1.90')
    """
    p = _to_decimal(price)
    w = _to_decimal(hourly_wage)
    if w == 0:
        raise ZeroDivisionError("hourly_wage must be > 0")
    h = p / w
    return h.quantize(Decimal(10) ** -precision)

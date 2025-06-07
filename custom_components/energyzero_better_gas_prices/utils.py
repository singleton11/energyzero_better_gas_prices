"""Utility functions for the EnergyZero Better Gas Prices integration."""

from decimal import ROUND_HALF_UP, Decimal


def round_monetary_value(value: float, decimal_places: int = 2) -> float | None:
    """Round monetary values using ROUND_HALF_UP method.

    Args:
        value: The value to round
        decimal_places: Number of decimal places to round to

    Returns:
        Rounded value as float

    """
    if value is None:
        return None
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
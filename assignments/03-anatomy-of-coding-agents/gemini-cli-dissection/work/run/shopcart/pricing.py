"""Pricing rules: discounts and tax. All amounts are integer cents."""
from __future__ import annotations

TAX_RATE = 0.08

# code -> (kind, value). "percent" values are whole percents; "fixed" values are cents.
DISCOUNT_CODES = {
    "SAVE10": ("percent", 10),
    "SAVE25": ("percent", 25),
    "TENOFF": ("fixed", 1000),
}


def validate_code(code: str) -> None:
    if code not in DISCOUNT_CODES:
        raise ValueError(f"invalid discount code: {code}")


def apply_discount(amount_cents: int, code: str | None) -> int:
    """Return the amount after applying a discount code. Never goes below zero."""
    if code is None:
        return amount_cents
    validate_code(code)
    kind, value = DISCOUNT_CODES[code]
    if kind == "percent":
        return round(amount_cents * (100 - value) / 100)
    return max(0, amount_cents - value)


def apply_tax(amount_cents: int) -> int:
    return round(amount_cents * (1 + TAX_RATE))


def calculate_shipping(subtotal_cents: int) -> int:
    """Return shipping fee in cents. Free if subtotal after discount is $50.00 (5000 cents) or more, or if empty (0)."""
    if subtotal_cents == 0:
        return 0
    if subtotal_cents >= 5000:
        return 0
    return 599


def final_total(subtotal_cents: int, code: str | None = None) -> int:
    """Total the customer pays for a given subtotal and optional discount code."""
    discounted = apply_discount(subtotal_cents, code)
    taxed = apply_tax(discounted)
    shipping = calculate_shipping(discounted)
    return taxed + shipping

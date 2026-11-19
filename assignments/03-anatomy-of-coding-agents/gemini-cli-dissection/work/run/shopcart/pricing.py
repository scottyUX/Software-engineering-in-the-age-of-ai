"""Pricing rules: discounts and tax. All amounts are integer cents."""
from __future__ import annotations

TAX_RATE = 0.08
SHIPPING_FEE_CENTS = 599
SHIPPING_THRESHOLD_CENTS = 5000

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


def calculate_shipping(discounted_subtotal_cents: int) -> int:
    """Return shipping fee in cents.
    - Flat $5.99 (599 cents) fee.
    - Free when subtotal after discount, before tax is $50.00 or more (>= 5000).
    - An empty cart pays no shipping (0).
    """
    if discounted_subtotal_cents == 0:
        return 0
    if discounted_subtotal_cents >= SHIPPING_THRESHOLD_CENTS:
        return 0
    return SHIPPING_FEE_CENTS


def final_total(subtotal_cents: int, code: str | None = None) -> int:
    """Total the customer pays for a given subtotal and optional discount code."""
    # Discount is applied before tax, and shipping is added (untaxed).
    discounted = apply_discount(subtotal_cents, code)
    taxed = apply_tax(discounted)
    shipping = calculate_shipping(discounted)
    return taxed + shipping

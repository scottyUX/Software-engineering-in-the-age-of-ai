import pytest

from shopcart.pricing import apply_discount, apply_tax, shipping_fee


def test_apply_tax():
    assert apply_tax(1000) == 1080


def test_no_code_means_no_discount():
    assert apply_discount(1000, None) == 1000


def test_percent_discount():
    assert apply_discount(2000, "SAVE25") == 1500


def test_fixed_discount_never_negative():
    assert apply_discount(500, "TENOFF") == 0


def test_invalid_code_raises():
    with pytest.raises(ValueError):
        apply_discount(1000, "BOGUS")


def test_shipping_fee_empty_cart():
    assert shipping_fee(0) == 0


def test_shipping_fee_under_threshold():
    assert shipping_fee(4999) == 599


def test_shipping_fee_at_threshold():
    assert shipping_fee(5000) == 0


def test_shipping_fee_above_threshold():
    assert shipping_fee(10000) == 0


def test_shipping_fee_with_discount_below_threshold():
    assert shipping_fee(6000, "SAVE25") == 599


def test_shipping_fee_with_discount_above_threshold():
    assert shipping_fee(8000, "SAVE10") == 0

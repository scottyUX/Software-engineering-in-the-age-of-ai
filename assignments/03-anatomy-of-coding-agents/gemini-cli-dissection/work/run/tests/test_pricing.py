import pytest

from shopcart.pricing import apply_discount, apply_tax, shipping_cost


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


def test_shipping_cost_rules():
    assert shipping_cost(0) == 0
    assert shipping_cost(-100) == 0
    assert shipping_cost(4999) == 599
    assert shipping_cost(5000) == 0
    assert shipping_cost(10000) == 0

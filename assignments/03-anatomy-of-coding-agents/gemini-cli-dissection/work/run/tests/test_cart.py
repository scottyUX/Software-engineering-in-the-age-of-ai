import pytest

from shopcart import Cart


def test_empty_cart_total_is_zero():
    assert Cart().total() == 0


def test_add_single_item():
    cart = Cart()
    cart.add_item("MUG")
    assert cart.items == {"MUG": 1}
    assert cart.subtotal() == 1200


def test_add_same_item_twice_increments_quantity():
    cart = Cart()
    cart.add_item("MUG")
    cart.add_item("MUG", 2)
    assert cart.items == {"MUG": 3}


def test_remove_item_decrements_then_deletes():
    cart = Cart()
    cart.add_item("CAP", 2)
    cart.remove_item("CAP")
    assert cart.items == {"CAP": 1}
    cart.remove_item("CAP")
    assert cart.items == {}


def test_unknown_sku_raises():
    with pytest.raises(ValueError):
        Cart().add_item("NOPE")


def test_invalid_code_raises():
    with pytest.raises(ValueError):
        Cart().apply_code("FREESTUFF")


def test_total_includes_tax():
    cart = Cart()
    cart.add_item("TEE")
    assert cart.total() == 2759  # 2000 + 8% tax + 599 shipping


def test_percent_discount():
    cart = Cart()
    cart.add_item("MUG", 2)
    cart.apply_code("SAVE10")
    assert cart.total() == 2932  # (2400 - 10%) + 8% tax + 599 shipping


def test_fixed_discount_applied_before_tax():
    cart = Cart()
    cart.add_item("TEE")
    cart.add_item("TEE")
    cart.apply_code("TENOFF")
    assert cart.total() == 3839  # (4000 - 1000) + 8% tax + 599 shipping


def test_shipping_free_above_threshold():
    cart = Cart()
    cart.add_item("TEE", 3)  # subtotal 6000 (>= 5000 threshold)
    assert cart.total() == 6480  # 6000 + 8% tax + 0 shipping


def test_shipping_fee_below_threshold():
    cart = Cart()
    cart.add_item("TEE", 2)  # subtotal 4000 (< 5000 threshold)
    assert cart.total() == 4919  # (4000 + 8% tax) + 599 shipping


def test_empty_cart_no_shipping():
    cart = Cart()
    assert cart.total() == 0

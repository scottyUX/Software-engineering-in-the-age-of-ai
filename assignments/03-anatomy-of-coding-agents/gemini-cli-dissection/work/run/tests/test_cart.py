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
    # Updated to include $5.99 shipping fee since subtotal < $50.00
    assert cart.total() == 2759  # 2000 + 8% tax + 599 shipping


def test_percent_discount():
    cart = Cart()
    cart.add_item("MUG", 2)
    cart.apply_code("SAVE10")
    # Updated to include $5.99 shipping fee since discounted subtotal < $50.00
    assert cart.total() == 2932  # ((2400 - 10%) + 8% tax) + 599 shipping


def test_fixed_discount_applied_before_tax():
    cart = Cart()
    cart.add_item("TEE")
    cart.add_item("TEE")
    cart.apply_code("TENOFF")
    # Updated to include $5.99 shipping fee since discounted subtotal < $50.00
    assert cart.total() == 3839  # ((4000 - 1000) + 8% tax) + 599 shipping


def test_free_shipping_threshold():
    cart = Cart()
    # 3 T-shirts = 6000 cents ($60.00), which is >= $50.00 threshold -> free shipping
    cart.add_item("TEE", 3)
    # 6000 + 8% tax = 6480, shipping = 0
    assert cart.total() == 6480


def test_free_shipping_with_discount():
    cart = Cart()
    # 3 T-shirts = 6000 cents, with SAVE10 (10% off) = 5400 cents ($54.00) >= $50.00 -> free shipping
    cart.add_item("TEE", 3)
    cart.apply_code("SAVE10")
    # 5400 + 8% tax = 5832, shipping = 0
    assert cart.total() == 5832

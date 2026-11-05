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


def test_shipping_fee_below_threshold():
    cart = Cart()
    cart.add_item("CAP", 2)  # 3000 cents (< 5000)
    # 3000 + 8% tax (3240) + 599 shipping = 3839
    assert cart.total() == 3839


def test_free_shipping_at_or_above_threshold():
    cart = Cart()
    cart.add_item("TEE", 3)  # 6000 cents (>= 5000)
    # 6000 + 8% tax (6480) + 0 shipping = 6480
    assert cart.total() == 6480


def test_free_shipping_via_discount():
    cart = Cart()
    cart.add_item("TEE", 3)  # 6000 cents
    cart.apply_code("SAVE25")  # 6000 - 25% = 4500 cents (< 5000)
    # Wait, 4500 is < 5000, so shipping should apply!
    # Let's test subtotal after discount >= 5000 vs < 5000.
    # What if subtotal is 6000, SAVE10 -> 5400 (>= 5000), free shipping!
    cart2 = Cart()
    cart2.add_item("TEE", 3)  # 6000
    cart2.apply_code("SAVE10")  # 5400 (>= 5000) -> 0 shipping
    # 5400 + 8% tax (5832) + 0 shipping = 5832
    assert cart2.total() == 5832

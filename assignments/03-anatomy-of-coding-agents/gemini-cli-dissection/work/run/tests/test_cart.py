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
    assert cart.total() == 2759  # 2000 + 8% tax + 5.99 shipping


def test_percent_discount():
    cart = Cart()
    cart.add_item("MUG", 2)
    cart.apply_code("SAVE10")
    assert cart.total() == 2932  # ((2400 - 10%) + 8% tax) + 5.99 shipping


def test_fixed_discount_applied_before_tax():
    cart = Cart()
    cart.add_item("TEE")
    cart.add_item("TEE")
    cart.apply_code("TENOFF")
    assert cart.total() == 3839  # ((4000 - 1000) + 8% tax) + 5.99 shipping


def test_shipping_fee_applied():
    cart = Cart()
    cart.add_item("MUG")  # 1200 subtotal (< 5000)
    # (1200 * 1.08) + 599 = 1296 + 599 = 1895
    assert cart.total() == 1895


def test_free_shipping_at_threshold():
    cart = Cart()
    # TEE (2) * 2000 + MUG (1) * 1200 = 5200
    cart.add_item("TEE", 2)
    cart.add_item("MUG")
    assert cart.subtotal() == 5200
    # 5200 + 8% tax (5616) + 0 shipping = 5616
    assert cart.total() == 5616


def test_free_shipping_after_discount():
    cart = Cart()
    cart.add_item("TEE", 3)  # 6000
    cart.apply_code("SAVE10")  # 10% off -> 5400 (>= 5000, free shipping)
    # 5400 + 8% tax = 5832
    assert cart.total() == 5832

    cart2 = Cart()
    cart2.add_item("TEE", 3)  # 6000
    cart2.apply_code("SAVE25")  # 25% off -> 4500 (< 5000, shipping applies)
    # 4500 + 8% tax (4860) + 599 shipping = 5459
    assert cart2.total() == 5459


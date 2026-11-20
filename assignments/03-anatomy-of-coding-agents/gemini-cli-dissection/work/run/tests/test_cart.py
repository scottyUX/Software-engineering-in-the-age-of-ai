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
    # 2000 + 8% tax + $5.99 shipping (subtotal $20.00 < $50.00 threshold)
    assert cart.total() == 2759  # 2160 tax-inclusive subtotal + 599 shipping


def test_percent_discount():
    cart = Cart()
    cart.add_item("MUG", 2)
    cart.apply_code("SAVE10")
    # (2400 - 10%) + 8% tax = 2333, plus $5.99 shipping (subtotal $21.60 discounted < $50.00)
    assert cart.total() == 2932  # 2333 + 599 shipping


def test_fixed_discount_applied_before_tax():
    cart = Cart()
    cart.add_item("TEE")
    cart.add_item("TEE")
    cart.apply_code("TENOFF")
    # (4000 - 1000) + 8% tax = 3240, plus $5.99 shipping (subtotal $30.00 discounted < $50.00)
    assert cart.total() == 3839  # 3240 + 599 shipping


def test_free_shipping_at_threshold():
    cart = Cart()
    # 3 T-shirts = 6000 cents ($60.00), which is >= $50.00 threshold
    cart.add_item("TEE", 3)
    # (6000) + 8% tax = 6480, shipping is free (0)
    assert cart.total() == 6480


def test_shipping_not_taxed():
    cart = Cart()
    # 2 T-shirts = 4000 cents ($40.00) -> subtotal < $50.00, so $5.99 shipping added
    cart.add_item("TEE", 2)
    # Tax on 4000 is 320 -> 4320. Plus 599 shipping = 4919.
    # If shipping were taxed (4000 + 599 = 4599 + 8%), it would be different.
    assert cart.total() == 4919


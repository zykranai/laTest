"""
Test Case 2 - Galaxy device cart workflow.

Assignment requirements covered:
- Navigate to Amazon.com
- Search for a Galaxy device
- Add the selected Galaxy device to the shopping cart
- Print the device price to the console
"""

import pytest

from page_objects.amazon_page import AmazonPage
from tests.test_data import GALAXY_SEARCH_KEYWORD
from utilities.price_validator import is_valid_price


@pytest.mark.amazon
def test_case_02_search_galaxy_and_add_to_cart(page) -> None:
    amazon = AmazonPage(page)

    device_price = amazon.search_add_to_cart_and_get_price(GALAXY_SEARCH_KEYWORD)

    # Assignment asks us to print the price to the console
    print(f"\n[Test Case 2] Galaxy device price added to cart: {device_price}")

    assert is_valid_price(device_price), (
        f"Expected a valid price after adding Galaxy device to cart, got: {device_price!r}"
    )

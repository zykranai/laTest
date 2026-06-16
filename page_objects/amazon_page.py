"""
Amazon Page Object.

This class wraps the common user actions required by the assignment:
open Amazon, search for a product, read the price, and add the item to cart.
"""

import re
from typing import Optional
from urllib.parse import quote_plus

from playwright.sync_api import Locator, Page, expect

from config.test_config import AMAZON_BASE_URL, AMAZON_ZIP_CODE, DEFAULT_TIMEOUT_MS
from utilities.price_validator import is_valid_price


class AmazonPage:
    """Page Object for Amazon.com product search and cart workflows."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.page.set_default_timeout(DEFAULT_TIMEOUT_MS)
        self._last_search_url: Optional[str] = None

    # -------------------------------------------------------------------------
    # Navigation helpers
    # -------------------------------------------------------------------------

    def open_home_page(self) -> None:
        """Navigate to Amazon and prepare the page for testing."""
        self.page.goto(AMAZON_BASE_URL, wait_until="domcontentloaded")
        expect(self.page.locator("#twotabsearchtextbox")).to_be_visible(
            timeout=DEFAULT_TIMEOUT_MS
        )

        self._close_common_popups()
        self._set_delivery_location_to_us()

    def _close_common_popups(self) -> None:
        """
        Close banners that appear on first visit.

        Amazon may show cookie consent or regional prompts depending on location.
        """
        cookie_button = self.page.locator("#sp-cc-accept")
        if cookie_button.is_visible(timeout=3000):
            cookie_button.click()
            self.page.wait_for_load_state("domcontentloaded")

        continue_shopping = self.page.get_by_role(
            "button", name=re.compile(r"continue shopping", re.I)
        )
        if continue_shopping.is_visible(timeout=2000):
            continue_shopping.click()

        stay_on_site = self.page.get_by_role(
            "button", name=re.compile(r"stay on amazon\.com", re.I)
        )
        if stay_on_site.is_visible(timeout=2000):
            stay_on_site.click()

    def _is_us_zip_set(self) -> bool:
        """Check whether the header already shows the configured US zip code."""
        location_label = self.page.locator("#glow-ingress-line2")
        if location_label.count() == 0:
            return False
        current_text = location_label.text_content() or ""
        return AMAZON_ZIP_CODE in current_text

    def _set_delivery_location_to_us(self) -> None:
        """
        Set a US zip code before shopping.

        Without a US delivery location, Amazon often hides prices and the
        add-to-cart button for international visitors.
        """
        if self._is_us_zip_set():
            return

        # Try twice — the first request establishes cookies, the second often sticks
        for _ in range(2):
            response = self.page.request.post(
                f"{AMAZON_BASE_URL}/gp/delivery/ajax/address-change.html",
                form={
                    "locationType": "LOCATION_INPUT",
                    "zipCode": AMAZON_ZIP_CODE,
                    "storeContext": "generic",
                    "deviceType": "web",
                    "pageType": "Gateway",
                    "actionSource": "glow",
                },
            )
            if not response.ok:
                continue

            self.page.goto(AMAZON_BASE_URL, wait_until="domcontentloaded")
            if self._is_us_zip_set():
                return

        raise AssertionError(
            f"Could not set US delivery location to zip code {AMAZON_ZIP_CODE}. "
            "Prices and add-to-cart may not be available."
        )

    # -------------------------------------------------------------------------
    # Search and product selection
    # -------------------------------------------------------------------------

    def search_product(self, keyword: str) -> None:
        """Search Amazon using the keyword and wait for results to load."""
        self._last_search_url = f"{AMAZON_BASE_URL}/s?k={quote_plus(keyword)}"
        self.page.goto(self._last_search_url, wait_until="domcontentloaded")

        results = self.page.locator('[data-component-type="s-search-result"]')
        expect(results.first).to_be_visible(timeout=DEFAULT_TIMEOUT_MS)

    def _return_to_search_results(self) -> None:
        """Go back to the search results page when a product row is not usable."""
        if self._last_search_url:
            self.page.goto(self._last_search_url, wait_until="domcontentloaded")
            return
        self.page.go_back(wait_until="domcontentloaded")

    def open_first_purchasable_product(self) -> str:
        """
        Open a product from the result list and return its price.

        The first result is not always purchasable (sponsored items, accessories,
        out-of-stock listings), so we try a few rows before failing.
        """
        results = self.page.locator('[data-component-type="s-search-result"]')
        expect(results.first).to_be_visible(timeout=DEFAULT_TIMEOUT_MS)

        for index in range(min(results.count(), 10)):
            result_row = results.nth(index)
            listing_price = self._extract_price_text(
                result_row.locator(".a-price .a-offscreen, .a-price-whole").first
            )

            product_link = self._get_product_link(result_row)
            if product_link is None:
                continue

            product_link.click()
            self.page.wait_for_load_state("domcontentloaded")

            try:
                product_price = self.read_product_price()
            except AssertionError:
                product_price = listing_price

            if not product_price or not is_valid_price(product_price):
                self._return_to_search_results()
                continue

            if not self._is_add_to_cart_available():
                self._return_to_search_results()
                continue

            return product_price

        raise AssertionError(
            "Could not find a product with a visible price and add-to-cart option."
        )

    def _get_product_link(self, result_row: Locator) -> Optional[Locator]:
        """Return the first usable product link inside a search result row."""
        link_selectors = [
            "a.a-link-normal[href*='/dp/']",
            ".s-title-instructions-style a",
            "a[href*='/dp/']",
        ]

        for selector in link_selectors:
            link = result_row.locator(selector).first
            if link.count() > 0 and link.is_visible():
                return link

        return None

    @staticmethod
    def _extract_price_text(price_locator: Locator) -> Optional[str]:
        """Safely read price text when the locator is present."""
        if price_locator.count() == 0:
            return None

        text = price_locator.text_content()
        if text and text.strip():
            return text.strip()

        return None

    def read_product_price(self) -> str:
        """Read the product price from the detail page."""
        price_selectors = [
            "#corePrice_feature_div .a-offscreen",
            "#corePriceDisplay_desktop_feature_div .a-offscreen",
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            "span.a-price span.a-offscreen",
            ".a-price .a-offscreen",
        ]

        for selector in price_selectors:
            price_element = self.page.locator(selector).first
            if price_element.count() > 0:
                price_text = price_element.text_content(timeout=5000)
                if price_text and price_text.strip():
                    cleaned_price = price_text.strip()
                    if "cannot be shipped" not in cleaned_price.lower():
                        return cleaned_price

        # Some pages split the price into whole and fraction spans
        whole_part = self.page.locator("span.a-price-whole").first
        fraction_part = self.page.locator("span.a-price-fraction").first
        if whole_part.count() > 0:
            price_value = whole_part.text_content() or ""
            if fraction_part.count() > 0:
                price_value += "." + (fraction_part.text_content() or "00")
            return f"${price_value.strip()}"

        raise AssertionError("Product price was not visible on the page.")

    # -------------------------------------------------------------------------
    # Cart actions
    # -------------------------------------------------------------------------

    def add_product_to_cart(self) -> None:
        """Click add to cart and verify that the action succeeded."""
        self._close_blocking_dialogs()
        self._choose_default_variants_if_needed()

        add_to_cart_button = self._find_add_to_cart_button()
        expect(add_to_cart_button).to_be_visible()
        add_to_cart_button.scroll_into_view_if_needed()

        try:
            add_to_cart_button.click(timeout=10000)
        except Exception:
            # Some product layouts need a forced click after variant selection
            add_to_cart_button.click(force=True)

        self._verify_item_added_to_cart()

    def _close_blocking_dialogs(self) -> None:
        """Close sponsored-content dialogs that can sit on top of the page."""
        close_buttons = self.page.get_by_role("button", name=re.compile(r"^close$", re.I))
        for index in range(close_buttons.count()):
            button = close_buttons.nth(index)
            if button.is_visible():
                button.click()

    def _choose_default_variants_if_needed(self) -> None:
        """
        Pick default color/size when Amazon requires a variant selection.

        Many phones and accessories won't enable add-to-cart until a variant is chosen.
        """
        dropdown_fields = self.page.locator(
            "#variation_color_name select, #variation_size_name select"
        )
        for index in range(dropdown_fields.count()):
            dropdown = dropdown_fields.nth(index)
            if dropdown.is_visible():
                options = dropdown.locator("option")
                if options.count() > 1:
                    dropdown.select_option(index=1)

        variant_tiles = self.page.locator(
            "#variation_color_name li, #variation_size_name li"
        )
        for index in range(min(variant_tiles.count(), 3)):
            tile = variant_tiles.nth(index)
            if tile.is_visible() and tile.get_attribute("aria-disabled") != "true":
                tile.click()
                break

    def _find_add_to_cart_button(self) -> Locator:
        """Locate the real add-to-cart button on the product page."""
        button_candidates = [
            self.page.locator("#add-to-cart-button").first,
            self.page.locator("#submit.add-to-cart-button").first,
            self.page.locator("input[name='submit.add-to-cart']").first,
        ]

        for candidate in button_candidates:
            if candidate.count() > 0 and candidate.is_visible():
                return candidate

        return self.page.locator("#add-to-cart-button").first

    def _is_add_to_cart_available(self) -> bool:
        """Check whether the current product page supports add-to-cart."""
        button = self.page.locator("#add-to-cart-button").first
        return button.count() > 0 and button.is_visible()

    def _verify_item_added_to_cart(self) -> None:
        """Confirm that Amazon acknowledged the add-to-cart action."""
        confirmation_selectors = [
            "#NATC_SMART_WAGON_CONF_MSG_SUCCESS",
            "#sw-atc-details-single-container",
            "#attachDisplayAddToCart",
            "#huc-v2-order-row-confirm-text",
            "span[data-action='sw-atc-confirmation-message']",
            "div.a-alert-content:has-text('Added to Cart')",
        ]

        for selector in confirmation_selectors:
            locator = self.page.locator(selector)
            if locator.count() > 0:
                return

        added_message = self.page.get_by_text(
            re.compile(r"added to (cart|your cart)", re.I)
        )
        expect(added_message.first).to_be_attached(timeout=DEFAULT_TIMEOUT_MS)

    # -------------------------------------------------------------------------
    # End-to-end flow used by both assignment test cases
    # -------------------------------------------------------------------------

    def search_add_to_cart_and_get_price(self, keyword: str) -> str:
        """
        Run the full assignment workflow for a given search keyword.

        Steps:
        1. Open Amazon
        2. Search for the product
        3. Open a valid result and read the price
        4. Add the product to cart
        """
        self.open_home_page()
        self.search_product(keyword)
        product_price = self.open_first_purchasable_product()
        self.add_product_to_cart()
        return product_price

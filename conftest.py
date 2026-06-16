"""
Shared pytest fixtures for browser setup.

Each test gets its own browser instance so Test Case 1 and Test Case 2
can run safely in parallel with pytest-xdist.
"""

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

from config import test_config
from utilities.lambdatest_helper import build_lambdatest_cdp_url, report_test_status


@pytest.fixture(scope="function")
def browser(request: pytest.FixtureRequest) -> Browser:
    """
    Start a local Chromium browser or connect to LambdaTest cloud.

    A function-scoped fixture keeps parallel workers isolated from each other.
    """
    test_name = request.node.name

    with sync_playwright() as playwright:
        if test_config.RUN_ON_LAMBDATEST:
            if not test_config.LT_USERNAME or not test_config.LT_ACCESS_KEY:
                pytest.skip(
                    "LambdaTest credentials missing. Set LT_USERNAME and LT_ACCESS_KEY."
                )

            browser = playwright.chromium.connect(
                build_lambdatest_cdp_url(test_name),
                timeout=60000,
            )
        else:
            browser = playwright.chromium.launch(headless=test_config.HEADLESS)

        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser: Browser, request: pytest.FixtureRequest) -> Page:
    """Provide a fresh browser tab for each test case."""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
    )
    page = context.new_page()

    yield page

    # Report final status to LambdaTest when running in cloud mode
    test_report = getattr(request.node, "rep_call", None)
    if test_report is not None and test_report.failed:
        report_test_status(page, "failed", str(test_report.longrepr))
    elif test_report is not None:
        report_test_status(page, "passed", "Test completed successfully")

    context.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    """
    Store the test result on the item object.

    This lets the page fixture know whether the test passed or failed.
    """
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

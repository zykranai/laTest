"""
LambdaTest integration helpers.

Reference: https://www.lambdatest.com/support/docs/playwright-testing/
"""

import json
import subprocess
import urllib.parse

from playwright.sync_api import Page

from config import test_config


def get_playwright_version() -> str:
    """Read the locally installed Playwright version for LambdaTest compatibility."""
    try:
        output = subprocess.check_output(
            ["playwright", "--version"], text=True, stderr=subprocess.STDOUT
        )
        return output.strip().split()[-1]
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        # Fallback keeps cloud runs working even if CLI lookup fails
        return "latest"


def build_lambdatest_cdp_url(test_name: str) -> str:
    """Build the WebSocket URL used to connect Playwright to LambdaTest."""
    capabilities = {
        "browserName": test_config.LT_BROWSER,
        "browserVersion": "latest",
        "LT:Options": {
            "platform": test_config.LT_PLATFORM,
            "build": test_config.LT_BUILD_NAME,
            "name": test_name,
            "user": test_config.LT_USERNAME,
            "accessKey": test_config.LT_ACCESS_KEY,
            "network": True,
            "video": True,
            "console": True,
            "playwrightClientVersion": get_playwright_version(),
        },
    }
    encoded_caps = urllib.parse.quote(json.dumps(capabilities))
    return f"wss://cdp.lambdatest.com/playwright?capabilities={encoded_caps}"


def report_test_status(page: Page, status: str, remark: str) -> None:
    """Send pass/fail status back to the LambdaTest dashboard."""
    if not test_config.RUN_ON_LAMBDATEST:
        return

    payload = json.dumps(
        {
            "action": "setTestStatus",
            "arguments": {"status": status, "remark": remark},
        }
    )
    page.evaluate(f"lambdatest_action: {payload}")

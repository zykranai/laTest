"""Helper functions for running Playwright tests on LambdaTest cloud."""

import json
import subprocess
import urllib.parse

from playwright.sync_api import Page

from config import test_config


def get_playwright_version() -> str:
    """Read local Playwright version to include in LambdaTest capabilities."""
    try:
        output = subprocess.check_output(
            ["playwright", "--version"], text=True, stderr=subprocess.STDOUT
        )
        return output.strip().split()[-1]
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        # Keep cloud runs working even if CLI lookup fails.
        return "latest"


def build_lambdatest_cdp_url(test_name: str) -> str:
    """Build the CDP WebSocket URL for LambdaTest execution."""
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
    """Send pass/fail status to the LambdaTest dashboard."""
    if not test_config.RUN_ON_LAMBDATEST:
        return

    payload = json.dumps(
        {
            "action": "setTestStatus",
            "arguments": {"status": status, "remark": remark},
        }
    )
    page.evaluate(f"lambdatest_action: {payload}")

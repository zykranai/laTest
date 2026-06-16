"""
Test configuration loaded from environment variables.

I kept all runtime settings in one place so local runs and LambdaTest cloud
runs can be switched without touching the test code.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root is one level above this config folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# --- Amazon test data ---
AMAZON_BASE_URL = os.getenv("AMAZON_BASE_URL", "https://www.amazon.com")
AMAZON_ZIP_CODE = os.getenv("AMAZON_ZIP_CODE", "10001")

# --- Browser behaviour ---
DEFAULT_TIMEOUT_MS = int(os.getenv("DEFAULT_TIMEOUT_MS", "30000"))
HEADLESS = os.getenv("HEADLESS", "true").lower() in {"1", "true", "yes"}

# --- LambdaTest cloud (bonus requirement) ---
RUN_ON_LAMBDATEST = os.getenv("RUN_ON_LAMBDATEST", "false").lower() in {"1", "true", "yes"}
LT_USERNAME = os.getenv("LT_USERNAME", "")
LT_ACCESS_KEY = os.getenv("LT_ACCESS_KEY", "")
LT_PLATFORM = os.getenv("LT_PLATFORM", "Windows 11")
LT_BROWSER = os.getenv("LT_BROWSER", "Chrome")
LT_BUILD_NAME = os.getenv("LT_BUILD_NAME", "Amazon Automation Assignment")

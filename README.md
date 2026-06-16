# Amazon Automation Assignment

Public repository for the **Automation Engineering Assignment** (Jun 2026).

This project automates two Amazon.com shopping scenarios using **Python**, **Playwright**, and **pytest**, with **parallel test execution** and optional **LambdaTest** cloud support.

**Repository:** [https://github.com/zykranai/laTest](https://github.com/zykranai/laTest)  
**Default branch:** `master`

GitHub Actions runs the parallel test suite automatically on every push to `master`.

---

## Assignment Coverage

| Test Case | File | Search Keyword | Verification |
|-----------|------|----------------|--------------|
| Test Case 1 | `tests/test_case_01_iphone_cart.py` | iPhone | Print device price to console |
| Test Case 2 | `tests/test_case_02_galaxy_cart.py` | Samsung Galaxy S24 | Print device price to console |

Both tests are designed to run **in parallel** using `pytest-xdist`.

---

## Project Structure

```text
laTest/
├── config/
│   └── test_config.py              # Environment and runtime settings
├── page_objects/
│   └── amazon_page.py              # Amazon Page Object Model
├── tests/
│   ├── test_data.py                # Shared search keywords
│   ├── test_case_01_iphone_cart.py # Assignment Test Case 1
│   └── test_case_02_galaxy_cart.py # Assignment Test Case 2
├── utilities/
│   └── lambdatest_helper.py        # LambdaTest cloud helpers
├── conftest.py                     # Browser fixtures
├── pytest.ini                      # Pytest configuration
├── requirements.txt                # Python dependencies
├── .env.example                    # Sample environment variables
└── README.md
```

---

## Prerequisites

- Python 3.9+
- pip
- Internet connection (tests run against live Amazon.com)

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/zykranai/laTest.git
cd laTest
git checkout master
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate       # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Configure environment variables (optional)

```bash
cp .env.example .env
```

Update `.env` only if you need custom timeouts, headless mode, or LambdaTest credentials.

---

## How to Run the Tests

### Parallel execution (required by assignment)

```bash
pytest -n 2
```

### Run with browser visible (helpful while debugging)

```bash
HEADLESS=false pytest -n 2 -s
```

### Run a single test case

```bash
pytest tests/test_case_01_iphone_cart.py -s
pytest tests/test_case_02_galaxy_cart.py -s
```

### Continuous Integration

Tests also run in GitHub Actions on push and pull requests to `master`.

- Workflow file: `.github/workflows/run-tests.yml`
- You can trigger a manual run from the **Actions** tab using **workflow_dispatch**

### Sample console output

```text
[Test Case 1] iPhone price added to cart: $279.42
[Test Case 2] Galaxy device price added to cart: $699.99
```

---

## LambdaTest Cloud Integration (Bonus)

1. Create a free account at [LambdaTest](https://www.lambdatest.com/).
2. Copy your username and access key from the [Automation Dashboard](https://accounts.lambdatest.com/dashboard).
3. Export the credentials:

```bash
export RUN_ON_LAMBDATEST=true
export LT_USERNAME="your_username"
export LT_ACCESS_KEY="your_access_key"
```

4. Run the suite in parallel on LambdaTest:

```bash
pytest -n 2
```

Test results, video, and logs will appear in the LambdaTest Web Automation dashboard.

---

## Design Approach

- **Page Object Model (POM)** keeps UI locators away from test files.
- **Separate test files** map directly to the two assignment test cases.
- **Shared config and test data** reduce duplication and make updates easier.
- **Parallel-safe fixtures** give each worker its own browser session.
- **US delivery setup** improves price visibility and add-to-cart reliability on Amazon.com.

---

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| Captcha / bot detection | Run with `HEADLESS=false` or use LambdaTest cloud |
| Timeout on search results | Increase `DEFAULT_TIMEOUT_MS` in `.env` |
| Price not found | Amazon UI changes often; rerun or adjust search keyword |
| LambdaTest auth failure | Verify `LT_USERNAME` and `LT_ACCESS_KEY` |

---

## Tech Stack

- Python 3
- Playwright
- pytest + pytest-xdist
- LambdaTest (optional cloud execution)

---

## Author

Automation Engineering Assignment — Jun 2026

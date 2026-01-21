# MB Secure Website Test Suite

Automated testing suite for the MB Secure website using Playwright and pytest.

## Quick Start

```bash
cd /Users/mb/Desktop/websites/mbsecure
source venv/bin/activate
python run_tests.py --browser chromium --no-report
```

## What's Tested

| Test File | What It Tests | Count |
|-----------|---------------|-------|
| `test_static.py` | Links, images, CSS/JS loading, meta tags | 44 |
| `test_browser.py` | Smooth scrolling, navigation, mobile menu, JS functionality | 25 |
| `test_responsive.py` | Layout at different screen sizes (desktop/tablet/mobile) | 21 |
| `test_visual.py` | Screenshot comparison to catch visual regressions | 18 |

**Total: 108 tests**

---

## Usage Workflows

### After Code Changes (HTML, CSS, JS)

```bash
source venv/bin/activate
python run_tests.py --browser chromium --no-report
```

- ✅ All pass → Changes are safe to deploy
- ❌ Failures → See output for what broke

### After Intentional Visual Changes

When you've deliberately changed the design (colors, layout, spacing, etc.):

```bash
source venv/bin/activate

# Step 1: Run visual tests to confirm what changed
python run_tests.py --visual-only --browser chromium --no-report

# Step 2: If failures are EXPECTED, update the baselines:
PLAYWRIGHT_UPDATE_SNAPSHOTS=1 python run_tests.py --visual-only --browser chromium --no-report

# Step 3: Verify new baselines pass
python run_tests.py --visual-only --browser chromium --no-report
```

### Quick Static Check (No Browser Needed)

For fast validation of links, assets, and HTML structure:

```bash
source venv/bin/activate
python run_tests.py --static-only --no-report
```

---

## Command Options

| Option | Description |
|--------|-------------|
| `--browser chromium` | Run with Chromium only (faster) |
| `--browser firefox` | Run with Firefox only |
| `--browser webkit` | Run with Safari/WebKit only |
| `--no-report` | Skip HTML report generation |
| `--static-only` | Only run static tests (no browser) |
| `--visual-only` | Only run visual regression tests |
| `-k "pattern"` | Run tests matching pattern |
| `-v` | Verbose output |
| `--headed` | Show browser window (for debugging) |

---

## Debugging Failed Tests

### Functional Test Failures

The output shows exactly what failed:

```
FAILED test_browser.py::TestSmoothScrolling::test_scroll_to_about_section
    AssertionError: Page did not scroll to about section
```

### Visual Test Failures

When a screenshot doesn't match:

```
FAILED test_visual.py::TestFullPageScreenshots::test_homepage_desktop
    Screenshot homepage-desktop.png differs by 2.5% (threshold: 0.1%)
    Actual saved to: tests/snapshots/homepage-desktop-actual.png
```

Compare the images:
```bash
open tests/snapshots/homepage-desktop.png         # Expected (baseline)
open tests/snapshots/homepage-desktop-actual.png  # Actual (current)
```

---

## Visual Baselines

Stored in `tests/snapshots/`. These are the "golden" screenshots tests compare against.

| Screenshot | Description |
|------------|-------------|
| `homepage-desktop.png` | Full homepage at 1280×720 |
| `homepage-mobile.png` | Full homepage at 375×667 |
| `blog-index-*.png` | Blog listing page |
| `blog-post-*.png` | Blog article page |
| `component-*.png` | Individual sections (header, hero, about, etc.) |

**Update baselines** after intentional design changes:
```bash
PLAYWRIGHT_UPDATE_SNAPSHOTS=1 python run_tests.py --visual-only --browser chromium --no-report
```

---

## Troubleshooting

### "No module named pytest"
```bash
source venv/bin/activate  # Forgot to activate venv
```

### Browser not installed
```bash
playwright install chromium firefox webkit
```

### Tests are slow
Use single browser instead of all three:
```bash
python run_tests.py --browser chromium --no-report
```

---

## Project Structure

```
mbsecure/
├── run_tests.py          # Test runner script
├── pyproject.toml        # Project configuration
├── pytest.ini            # Pytest settings
├── venv/                 # Python virtual environment
└── tests/
    ├── conftest.py       # Fixtures (local server, browser)
    ├── test_static.py    # Link/asset tests
    ├── test_browser.py   # JavaScript functionality tests
    ├── test_responsive.py # Responsive layout tests
    ├── test_visual.py    # Visual regression tests
    └── snapshots/        # Baseline screenshots
```

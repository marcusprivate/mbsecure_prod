"""
Visual regression tests using Playwright screenshots.
Captures full-page and component screenshots for comparison.
Uses pytest-playwright's screenshot comparison with threshold.
"""
import pytest
import re
from playwright.sync_api import Page
from pathlib import Path
from PIL import Image
import io
import os

# Import shared test configuration
from tests.conftest import BLOG_POSTS


# Viewport sizes for screenshots
DESKTOP_VIEWPORT = {"width": 1280, "height": 720}
MOBILE_VIEWPORT = {"width": 375, "height": 667}

# Snapshot directory
SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


def blog_post_to_snapshot_name(blog_path: str) -> str:
    """Convert a blog post path to a valid snapshot filename.
    
    Example: /blog/2020/4/the-sources-for-hunts.html -> blog-2020-4-the-sources-for-hunts
    """
    # Remove leading slash and .html extension
    name = blog_path.lstrip('/').replace('.html', '')
    # Replace path separators with dashes
    name = name.replace('/', '-')
    return name


def compare_screenshots(actual_bytes: bytes, expected_path: Path, threshold: float = 0.1) -> tuple[bool, float]:
    """
    Compare two screenshots and return if they match within threshold.
    
    Args:
        actual_bytes: The actual screenshot bytes
        expected_path: Path to the expected baseline image
        threshold: Maximum allowed difference percentage (0-100)
    
    Returns:
        Tuple of (matches, diff_percentage)
    """
    if not expected_path.exists():
        return False, 100.0
    
    actual_img = Image.open(io.BytesIO(actual_bytes))
    expected_img = Image.open(expected_path)
    
    # Convert to same mode if different
    if actual_img.mode != expected_img.mode:
        actual_img = actual_img.convert('RGB')
        expected_img = expected_img.convert('RGB')
    
    # Check dimensions
    if actual_img.size != expected_img.size:
        return False, 100.0
    
    # Calculate pixel differences
    actual_pixels = list(actual_img.tobytes())
    expected_pixels = list(expected_img.tobytes())
    
    total_pixels = len(actual_pixels)
    diff_count = sum(1 for a, e in zip(actual_pixels, expected_pixels) if a != e)
    
    diff_percentage = (diff_count / total_pixels) * 100
    matches = diff_percentage <= threshold
    
    return matches, diff_percentage


def save_screenshot(screenshot_bytes: bytes, path: Path):
    """Save screenshot bytes to file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(screenshot_bytes)


def assert_screenshot(page_or_locator, name: str, full_page: bool = False, threshold: float = 0.1):
    """
    Assert that a screenshot matches the baseline or create it if missing.
    
    On first run (no baseline), saves the screenshot as the new baseline.
    On subsequent runs, compares against the baseline.
    
    Set PLAYWRIGHT_UPDATE_SNAPSHOTS=1 env var to update baselines.
    """
    expected_path = SNAPSHOT_DIR / name
    
    # Take screenshot - full_page only works for Page, not Locator
    if full_page:
        screenshot_bytes = page_or_locator.screenshot(
            full_page=True,
            animations="disabled"
        )
    else:
        screenshot_bytes = page_or_locator.screenshot(
            animations="disabled"
        )
    
    # Check if we should update snapshots
    update_snapshots = os.environ.get("PLAYWRIGHT_UPDATE_SNAPSHOTS", "").lower() in ("1", "true", "yes")
    
    if not expected_path.exists() or update_snapshots:
        # Save as new baseline
        save_screenshot(screenshot_bytes, expected_path)
        if not update_snapshots:
            pytest.skip(f"Baseline created: {name}. Run again to compare.")
        return
    
    # Compare with baseline
    matches, diff_percentage = compare_screenshots(screenshot_bytes, expected_path, threshold)
    
    if not matches:
        # Save actual and diff for debugging
        actual_path = SNAPSHOT_DIR / f"{name.replace('.png', '')}-actual.png"
        save_screenshot(screenshot_bytes, actual_path)
        pytest.fail(f"Screenshot {name} differs by {diff_percentage:.2f}% (threshold: {threshold}%). "
                   f"Actual saved to: {actual_path}")


class TestFullPageScreenshots:
    """Full-page visual regression tests."""
    
    def test_homepage_desktop(self, page: Page, local_server):
        """Capture full homepage screenshot at desktop size."""
        page.set_viewport_size(DESKTOP_VIEWPORT)
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.wait_for_timeout(500)
        
        assert_screenshot(page, "homepage-desktop.png", full_page=True)
    
    def test_homepage_mobile(self, page: Page, local_server):
        """Capture full homepage screenshot at mobile size."""
        page.set_viewport_size(MOBILE_VIEWPORT)
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.wait_for_timeout(500)
        
        assert_screenshot(page, "homepage-mobile.png", full_page=True)
    
    def test_blog_index_desktop(self, page: Page, local_server):
        """Capture blog index page screenshot at desktop size."""
        page.set_viewport_size(DESKTOP_VIEWPORT)
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.wait_for_timeout(500)
        
        assert_screenshot(page, "blog-index-desktop.png", full_page=True)
    
    def test_blog_index_mobile(self, page: Page, local_server):
        """Capture blog index page screenshot at mobile size."""
        page.set_viewport_size(MOBILE_VIEWPORT)
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.wait_for_timeout(500)
        
        assert_screenshot(page, "blog-index-mobile.png", full_page=True)
    
    @pytest.mark.parametrize("blog_post", BLOG_POSTS)
    def test_blog_post_desktop(self, page: Page, local_server, blog_post):
        """Capture blog post page screenshot at desktop size."""
        page.set_viewport_size(DESKTOP_VIEWPORT)
        page.goto(f"{local_server}{blog_post}")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.wait_for_timeout(500)
        
        snapshot_name = f"{blog_post_to_snapshot_name(blog_post)}-desktop.png"
        assert_screenshot(page, snapshot_name, full_page=True)
    
    @pytest.mark.parametrize("blog_post", BLOG_POSTS)
    def test_blog_post_mobile(self, page: Page, local_server, blog_post):
        """Capture blog post page screenshot at mobile size."""
        page.set_viewport_size(MOBILE_VIEWPORT)
        page.goto(f"{local_server}{blog_post}")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.wait_for_timeout(500)
        
        snapshot_name = f"{blog_post_to_snapshot_name(blog_post)}-mobile.png"
        assert_screenshot(page, snapshot_name, full_page=True)


class TestComponentScreenshots:
    """Component-level visual regression tests."""
    
    def test_nav_component(self, page: Page, local_server):
        """Capture nav component screenshot."""
        page.set_viewport_size(DESKTOP_VIEWPORT)
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.wait_for_timeout(500)
        
        nav = page.locator("#nav")
        assert_screenshot(nav, "component-nav.png")
    
    def test_hero_section_component(self, page: Page, local_server):
        """Capture hero section component screenshot."""
        page.set_viewport_size(DESKTOP_VIEWPORT)
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.wait_for_timeout(500)
        
        hero = page.locator("#hero")
        assert_screenshot(hero, "component-hero.png")
    
    def test_about_section_component(self, page: Page, local_server):
        """Capture about section component screenshot."""
        page.set_viewport_size(DESKTOP_VIEWPORT)
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.evaluate("document.querySelector('#about').scrollIntoView()")
        page.wait_for_timeout(500)
        
        about = page.locator("#about")
        assert_screenshot(about, "component-about.png")
    
    def test_services_page_component(self, page: Page, local_server):
        """Capture services page component screenshot."""
        page.set_viewport_size(DESKTOP_VIEWPORT)
        page.goto(f"{local_server}/services/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.wait_for_timeout(500)
        
        services = page.locator("#services")
        assert_screenshot(services, "component-services-page.png")
    
    def test_contact_section_component(self, page: Page, local_server):
        """Capture contact section component screenshot."""
        page.set_viewport_size(DESKTOP_VIEWPORT)
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.evaluate("document.querySelector('#contact').scrollIntoView()")
        page.wait_for_timeout(500)
        
        contact = page.locator("#contact")
        assert_screenshot(contact, "component-contact.png")
    
    def test_footer_component(self, page: Page, local_server):
        """Capture footer component screenshot."""
        page.set_viewport_size(DESKTOP_VIEWPORT)
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.evaluate("document.querySelector('#footer').scrollIntoView()")
        page.wait_for_timeout(500)
        
        footer = page.locator("#footer")
        assert_screenshot(footer, "component-footer.png")


class TestMobileComponentScreenshots:
    """Mobile component visual regression tests."""
    
    def test_mobile_titlebar_component(self, page: Page, local_server):
        """Capture mobile titlebar component screenshot."""
        page.set_viewport_size(MOBILE_VIEWPORT)
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.wait_for_timeout(500)
        
        titlebar = page.locator("#titleBar")
        assert_screenshot(titlebar, "component-mobile-titlebar.png")
    
    def test_mobile_nav_panel_open(self, page: Page, local_server):
        """Capture mobile nav panel when open."""
        page.set_viewport_size(MOBILE_VIEWPORT)
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        
        # Open nav panel
        page.click("#titleBar .toggle")
        page.wait_for_timeout(500)
        
        nav_panel = page.locator("#navPanel")
        assert_screenshot(nav_panel, "component-mobile-nav-panel.png")


class TestBlogComponentScreenshots:
    """Blog component visual regression tests."""
    
    def test_blog_card_component(self, page: Page, local_server):
        """Capture blog card component screenshot."""
        page.set_viewport_size(DESKTOP_VIEWPORT)
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.wait_for_timeout(500)
        
        blog_card = page.locator(".blog-card").first
        if blog_card.count() > 0:
            assert_screenshot(blog_card, "component-blog-card.png")
    
    def test_blog_article_component(self, page: Page, local_server):
        """Capture blog article component screenshot."""
        page.set_viewport_size(DESKTOP_VIEWPORT)
        page.goto(f"{local_server}/blog/2020/4/the-sources-for-hunts-and-how-to-prioritise.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.wait_for_timeout(500)
        
        article = page.locator("article")
        assert_screenshot(article, "component-blog-article.png")


class TestInteractionStateScreenshots:
    """Visual tests for interaction states."""
    
    def test_nav_hover_state(self, page: Page, local_server):
        """Capture navigation with hover state."""
        page.set_viewport_size(DESKTOP_VIEWPORT)
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.wait_for_timeout(500)
        
        # Hover over About link
        about_link = page.locator("#nav a[href='#about']")
        about_link.hover()
        page.wait_for_timeout(300)
        
        nav = page.locator("#nav")
        assert_screenshot(nav, "component-nav-hover.png")
    
    def test_scrolled_state(self, page: Page, local_server):
        """Capture page in scrolled state."""
        page.set_viewport_size(DESKTOP_VIEWPORT)
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(1000)
        
        page.evaluate("document.body.classList.remove('is-preload')")
        page.evaluate("window.scrollTo(0, 500)")
        page.wait_for_timeout(500)
        
        assert_screenshot(page, "homepage-scrolled.png")

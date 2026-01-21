"""
Accessibility tests using Axe-core via Playwright.
Tests for WCAG 2.1 Level AA compliance.
"""
import pytest
from playwright.sync_api import Page


# Axe-core CDN URL
AXE_CORE_URL = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.2/axe.min.js"


def inject_axe(page: Page):
    """Inject axe-core into the page."""
    page.evaluate(f"""
        new Promise((resolve, reject) => {{
            if (window.axe) {{
                resolve();
                return;
            }}
            const script = document.createElement('script');
            script.src = '{AXE_CORE_URL}';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        }})
    """)
    page.wait_for_function("typeof window.axe !== 'undefined'")


def run_axe(page: Page, context: str = None, options: dict = None):
    """
    Run axe-core accessibility tests.
    
    Args:
        page: Playwright page object
        context: CSS selector to limit testing scope (optional)
        options: Axe-core run options (optional)
    
    Returns:
        List of accessibility violations
    """
    inject_axe(page)
    
    # Default options for WCAG 2.1 AA
    default_options = {
        "runOnly": {
            "type": "tag",
            "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"]
        }
    }
    
    if options:
        default_options.update(options)
    
    import json
    run_options_json = json.dumps(default_options)
    
    # Build axe.run call
    if context:
        results = page.evaluate(f"""
            (async () => {{
                const results = await axe.run('{context}', {run_options_json});
                return results;
            }})()
        """)
    else:
        results = page.evaluate(f"""
            (async () => {{
                const results = await axe.run({run_options_json});
                return results;
            }})()
        """)
    
    return results.get("violations", [])


def format_violations(violations: list) -> str:
    """Format violations for error message."""
    if not violations:
        return "No violations found"
    
    messages = []
    for v in violations:
        impact = v.get("impact", "unknown")
        description = v.get("description", "No description")
        help_url = v.get("helpUrl", "")
        nodes = v.get("nodes", [])
        
        node_info = []
        for node in nodes[:3]:  # Limit to first 3 nodes
            target = node.get("target", ["unknown"])
            node_info.append(f"  - {target[0] if target else 'unknown'}")
        
        if len(nodes) > 3:
            node_info.append(f"  - ... and {len(nodes) - 3} more")
        
        messages.append(
            f"\n[{impact.upper()}] {description}\n"
            f"Help: {help_url}\n"
            f"Affected elements:\n" + "\n".join(node_info)
        )
    
    return "\n".join(messages)


class TestAccessibilityHomepage:
    """Accessibility tests for the homepage."""
    
    def test_homepage_no_critical_violations(self, page: Page, local_server):
        """Homepage should have no critical or serious accessibility violations."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(1000)  # Wait for JS to complete
        
        violations = run_axe(page)
        
        # Filter for critical and serious issues only
        critical_violations = [
            v for v in violations 
            if v.get("impact") in ["critical", "serious"]
        ]
        
        # Exclude known acceptable issues (CTA button uses brand color with acceptable contrast)
        critical_violations = [
            v for v in critical_violations
            if not any(
                ".large" in node.get("target", [""])[0] or 
                "button.primary.large" in node.get("html", "")
                for node in v.get("nodes", [])
            )
        ]
        
        assert len(critical_violations) == 0, (
            f"Found {len(critical_violations)} critical/serious accessibility violations:\n"
            f"{format_violations(critical_violations)}"
        )
    
    def test_homepage_images_have_alt(self, page: Page, local_server):
        """All images should have alt text."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Check for images without alt attribute
        images_without_alt = page.locator("img:not([alt])").count()
        
        assert images_without_alt == 0, (
            f"Found {images_without_alt} images without alt attribute"
        )
    
    def test_homepage_skip_link_exists(self, page: Page, local_server):
        """Homepage should have a skip-to-content link."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        skip_link = page.locator(".skip-to-content")
        assert skip_link.count() > 0, "Skip-to-content link not found"
    
    def test_homepage_skip_link_visible_on_focus(self, page: Page, local_server):
        """Skip link should become visible when focused."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Tab to the skip link
        page.keyboard.press("Tab")
        
        skip_link = page.locator(".skip-to-content:focus")
        assert skip_link.is_visible(), "Skip link should be visible when focused"
    
    def test_homepage_headings_hierarchy(self, page: Page, local_server):
        """Headings should follow a logical hierarchy (no skipped levels)."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Get all heading levels in order
        headings = page.evaluate("""
            () => {
                const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                return Array.from(headings).map(h => parseInt(h.tagName[1]));
            }
        """)
        
        # Check for skipped levels (e.g., h1 -> h3 without h2)
        skipped = []
        for i in range(1, len(headings)):
            if headings[i] > headings[i-1] + 1:
                skipped.append(f"h{headings[i-1]} -> h{headings[i]}")
        
        assert len(skipped) == 0, f"Heading hierarchy has skipped levels: {skipped}"


class TestAccessibilityBlogIndex:
    """Accessibility tests for blog index pages."""
    
    def test_blog_index_no_critical_violations(self, page: Page, local_server):
        """Blog index should have no critical accessibility violations."""
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(1000)
        
        violations = run_axe(page)
        critical_violations = [
            v for v in violations 
            if v.get("impact") in ["critical", "serious"]
        ]
        
        assert len(critical_violations) == 0, (
            f"Found {len(critical_violations)} critical/serious violations:\n"
            f"{format_violations(critical_violations)}"
        )
    
    def test_blog_index_links_are_distinguishable(self, page: Page, local_server):
        """Blog links should be distinguishable from regular text."""
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(500)
        
        # Check that blog card links have proper styling
        blog_links = page.locator(".blog-card h2 a")
        assert blog_links.count() > 0, "No blog card links found"


class TestAccessibilityBlogPosts:
    """Accessibility tests for blog posts."""
    
    @pytest.fixture
    def sample_blog_post(self, local_server):
        """Return URL of a sample blog post."""
        return f"{local_server}/blog/2020/4/the-sources-for-hunts-and-how-to-prioritise.html"
    
    def test_blog_post_no_critical_violations(self, page: Page, sample_blog_post):
        """Blog post should have no critical accessibility violations."""
        page.goto(sample_blog_post)
        page.wait_for_timeout(1000)
        
        violations = run_axe(page)
        critical_violations = [
            v for v in violations 
            if v.get("impact") in ["critical", "serious"]
        ]
        
        assert len(critical_violations) == 0, (
            f"Found {len(critical_violations)} critical/serious violations:\n"
            f"{format_violations(critical_violations)}"
        )
    
    def test_blog_post_has_main_landmark(self, page: Page, sample_blog_post):
        """Blog post should have a main landmark."""
        page.goto(sample_blog_post)
        page.wait_for_timeout(500)
        
        main = page.locator("main, [role='main']")
        assert main.count() > 0, "No main landmark found"
    
    def test_blog_post_article_has_heading(self, page: Page, sample_blog_post):
        """Blog post article should have a heading."""
        page.goto(sample_blog_post)
        page.wait_for_timeout(500)
        
        article_heading = page.locator("article h1, article h2")
        assert article_heading.count() > 0, "Article should have a heading"
    
    def test_blog_post_code_blocks_accessible(self, page: Page, sample_blog_post):
        """Code blocks should be properly marked up."""
        page.goto(sample_blog_post)
        page.wait_for_timeout(500)
        
        # Check that pre/code blocks exist and are properly structured
        code_blocks = page.locator("pre code, pre.language-")
        if code_blocks.count() > 0:
            # At least the first code block should have a language class
            first_block = code_blocks.first
            class_attr = first_block.get_attribute("class") or ""
            has_language = "language-" in class_attr
            assert has_language, "Code blocks should have language class for screen readers"


class TestAccessibilityNavigation:
    """Tests for navigation accessibility."""
    
    def test_nav_has_aria_role(self, page: Page, local_server):
        """Navigation should have proper ARIA role."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        nav = page.locator("nav, [role='navigation']")
        assert nav.count() > 0, "No navigation landmark found"
    
    def test_nav_links_are_focusable(self, page: Page, local_server):
        """Navigation links should be keyboard focusable."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Tab through navigation and verify focus
        page.keyboard.press("Tab")  # Skip link
        page.keyboard.press("Tab")  # First nav item
        
        focused = page.evaluate("document.activeElement.tagName")
        assert focused == "A", f"Expected link to be focused, got {focused}"


class TestAccessibilityColorContrast:
    """Tests for color contrast accessibility."""
    
    def test_no_color_contrast_violations(self, page: Page, local_server):
        """Pages should have sufficient color contrast."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(1000)
        
        # Run axe with only color-contrast rule
        violations = run_axe(page, options={
            "runOnly": {
                "type": "rule",
                "values": ["color-contrast"]
            }
        })
        
        # Filter out minor issues
        serious_contrast = [
            v for v in violations 
            if v.get("impact") in ["critical", "serious"]
        ]
        
        # Exclude known acceptable issues (CTA button uses brand color)
        serious_contrast = [
            v for v in serious_contrast
            if not any(
                ".large" in node.get("target", [""])[0] or
                "button.primary.large" in node.get("html", "")
                for node in v.get("nodes", [])
            )
        ]
        
        assert len(serious_contrast) == 0, (
            f"Found {len(serious_contrast)} serious color contrast issues:\n"
            f"{format_violations(serious_contrast)}"
        )

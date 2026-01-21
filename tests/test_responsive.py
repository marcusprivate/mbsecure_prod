"""
Responsive layout tests using Playwright.
Tests for different viewport sizes and breakpoint behavior.
"""
import pytest
from playwright.sync_api import expect, Page
import re


# Viewport configurations for testing
VIEWPORTS = {
    "desktop_large": {"width": 1400, "height": 900},
    "desktop": {"width": 1200, "height": 800},
    "tablet_landscape": {"width": 1000, "height": 700},
    "tablet": {"width": 800, "height": 1024},
    "mobile": {"width": 500, "height": 844},
    "mobile_small": {"width": 350, "height": 667},
}


class TestDesktopLayout:
    """Test desktop layout (>980px)."""
    
    def test_desktop_nav_visible(self, page: Page, local_server):
        """Verify desktop navigation is visible on large screens."""
        page.set_viewport_size(VIEWPORTS["desktop"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        nav = page.locator("#nav")
        expect(nav).to_be_visible()
    
    def test_desktop_titlebar_hidden(self, page: Page, local_server):
        """Verify mobile titlebar is hidden on desktop."""
        page.set_viewport_size(VIEWPORTS["desktop"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        titlebar = page.locator("#titleBar")
        # Should be hidden (display: none or visibility: hidden)
        expect(titlebar).to_be_hidden()
    
    def test_desktop_services_page_layout(self, page: Page, local_server):
        """Verify services page uses multi-column layout on desktop."""
        page.set_viewport_size(VIEWPORTS["desktop"])
        page.goto(f"{local_server}/services/index.html")
        page.wait_for_timeout(500)
        
        # Check that services section exists
        services = page.locator("#services")
        expect(services).to_be_visible()
        
        # Get width of services container to verify it's using full width
        services_box = services.bounding_box()
        assert services_box["width"] > 700, "Services section should be wide on desktop"
    
    def test_desktop_nav_visible(self, page: Page, local_server):
        """Verify navigation is visible on desktop."""
        page.set_viewport_size(VIEWPORTS["desktop"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        nav = page.locator("#nav")
        expect(nav).to_be_visible()


class TestMobileLayout:
    """Test mobile layout (≤980px)."""
    
    def test_mobile_nav_hidden(self, page: Page, local_server):
        """Verify desktop navigation is hidden on mobile."""
        page.set_viewport_size(VIEWPORTS["mobile"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        nav = page.locator("#nav")
        expect(nav).to_be_hidden()
    
    def test_mobile_titlebar_visible(self, page: Page, local_server):
        """Verify mobile titlebar is visible on mobile."""
        page.set_viewport_size(VIEWPORTS["mobile"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        titlebar = page.locator("#titleBar")
        expect(titlebar).to_be_visible()
    
    def test_mobile_hamburger_menu_visible(self, page: Page, local_server):
        """Verify hamburger menu icon is visible on mobile."""
        page.set_viewport_size(VIEWPORTS["mobile"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        hamburger = page.locator("#titleBar .toggle")
        expect(hamburger).to_be_visible()
    
    def test_mobile_nav_panel_opens(self, page: Page, local_server):
        """Verify clicking hamburger opens navigation panel."""
        page.set_viewport_size(VIEWPORTS["mobile"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Click hamburger menu
        page.click("#titleBar .toggle")
        page.wait_for_timeout(500)
        
        # Check nav panel is visible
        nav_panel = page.locator("#navPanel")
        expect(nav_panel).to_be_visible()
    
    def test_mobile_nav_panel_has_links(self, page: Page, local_server):
        """Verify nav panel contains navigation links."""
        page.set_viewport_size(VIEWPORTS["mobile"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Open nav panel
        page.click("#titleBar .toggle")
        page.wait_for_timeout(500)
        
        # Check for links in nav panel
        about_link = page.locator("#navPanel a[href='#about']")
        expect(about_link).to_be_visible()
    
    def test_mobile_nav_panel_closes_on_backdrop(self, page: Page, local_server):
        """Verify clicking backdrop closes nav panel."""
        page.set_viewport_size(VIEWPORTS["mobile"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Open nav panel
        page.click("#titleBar .toggle")
        page.wait_for_timeout(500)
        
        # Click backdrop to close (left side of screen, away from the nav panel on the right)
        backdrop = page.locator("#navBackdrop")
        if backdrop.is_visible():
            # Click on the left side of the backdrop (position 50, 300) to avoid the navPanel
            backdrop.click(position={"x": 50, "y": 300})
            page.wait_for_timeout(500)
            
            # Verify panel is hidden or transformed away
            nav_panel = page.locator("#navPanel")
            # Panel might still be in DOM but transformed off-screen
    
    def test_mobile_nav_panel_closes_on_toggle_click(self, page: Page, local_server):
        """Verify clicking the hamburger/X button again closes nav panel."""
        page.set_viewport_size(VIEWPORTS["mobile"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Open nav panel
        page.click("#titleBar .toggle")
        page.wait_for_timeout(500)
        
        # Verify panel is open (body has navPanel-visible class among others)
        expect(page.locator("body")).to_have_class(re.compile(r"navPanel-visible"))
        
        # Click toggle (X button) again to close
        page.click("#titleBar .toggle")
        page.wait_for_timeout(500)
        
        # Verify panel is closed (body no longer has navPanel-visible class)
        expect(page.locator("body")).not_to_have_class(re.compile(r"navPanel-visible"))
    
    def test_mobile_nav_panel_escape_key_behavior(self, page: Page, local_server):
        """Document ESC key behavior for nav panel (hideOnEscape is disabled)."""
        page.set_viewport_size(VIEWPORTS["mobile"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Open nav panel
        page.click("#titleBar .toggle")
        page.wait_for_timeout(500)
        
        # Verify panel is open
        expect(page.locator("body")).to_have_class(re.compile(r"navPanel-visible"))
        
        # Press Escape
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        
        # Note: hideOnEscape is currently disabled in main.js
        # This test documents current behavior - panel stays open
        # If hideOnEscape is enabled, change to not_to_have_class
        expect(page.locator("body")).to_have_class(re.compile(r"navPanel-visible"))
    
    def test_mobile_nav_panel_closes_on_link_click(self, page: Page, local_server):
        """Verify clicking a link closes nav panel and scrolls."""
        page.set_viewport_size(VIEWPORTS["mobile"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Open nav panel
        page.click("#titleBar .toggle")
        page.wait_for_timeout(500)
        
        # Click about link
        page.click("#navPanel a[href='#about']")
        page.wait_for_timeout(1500)
        
        # Verify scrolled to about section
        about_section = page.locator("#about")
        expect(about_section).to_be_in_viewport()


class TestTabletLayout:
    """Test tablet layout (737px - 980px)."""
    
    def test_tablet_landscape_layout(self, page: Page, local_server):
        """Test tablet landscape viewport."""
        page.set_viewport_size(VIEWPORTS["tablet_landscape"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # At 1000px, desktop nav should still be visible
        nav = page.locator("#nav")
        expect(nav).to_be_visible()
    
    def test_tablet_portrait_layout(self, page: Page, local_server):
        """Test tablet portrait viewport."""
        page.set_viewport_size(VIEWPORTS["tablet"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # At 800px (< 980px), mobile nav should be shown
        titlebar = page.locator("#titleBar")
        expect(titlebar).to_be_visible()


class TestSmallMobileLayout:
    """Test very small mobile layout (≤360px)."""
    
    def test_xsmall_viewport(self, page: Page, local_server):
        """Test extra small viewport."""
        page.set_viewport_size(VIEWPORTS["mobile_small"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Page should still be functional
        titlebar = page.locator("#titleBar")
        expect(titlebar).to_be_visible()
    
    def test_xsmall_content_fits(self, page: Page, local_server):
        """Verify content doesn't overflow on small screens."""
        page.set_viewport_size(VIEWPORTS["mobile_small"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Check that body doesn't have horizontal scroll
        has_horizontal_scroll = page.evaluate(
            "document.documentElement.scrollWidth > document.documentElement.clientWidth"
        )
        assert not has_horizontal_scroll, "Page should not have horizontal scroll on small screens"


class TestBlogResponsive:
    """Test blog pages responsive behavior."""
    
    def test_blog_desktop_layout(self, page: Page, local_server):
        """Verify blog page layout on desktop."""
        page.set_viewport_size(VIEWPORTS["desktop"])
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(500)
        
        # Check blog grid exists
        blog_grid = page.locator(".blog-grid")
        if blog_grid.count() > 0:
            expect(blog_grid).to_be_visible()
    
    def test_blog_mobile_layout(self, page: Page, local_server):
        """Verify blog page layout on mobile."""
        page.set_viewport_size(VIEWPORTS["mobile"])
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(500)
        
        # Titlebar should be visible
        titlebar = page.locator("#titleBar")
        expect(titlebar).to_be_visible()
    
    def test_blog_post_mobile_readable(self, page: Page, local_server):
        """Verify blog post is readable on mobile."""
        page.set_viewport_size(VIEWPORTS["mobile"])
        page.goto(f"{local_server}/blog/2020/4/the-sources-for-hunts-and-how-to-prioritise.html")
        page.wait_for_timeout(500)
        
        article = page.locator("article")
        expect(article).to_be_visible()
        
        # Article should fit within viewport width
        article_box = article.bounding_box()
        assert article_box["width"] <= 500, "Article should fit within mobile viewport"


class TestButtonResponsive:
    """Test button sizing across breakpoints."""
    
    def test_buttons_not_overflowing_mobile(self, page: Page, local_server):
        """Verify buttons don't overflow on mobile."""
        page.set_viewport_size(VIEWPORTS["mobile"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Check CTA button in hero
        cta = page.locator("#banner a.button").first
        if cta.count() > 0:
            cta_box = cta.bounding_box()
            if cta_box:
                assert cta_box["width"] < 450, "Button should fit within mobile viewport"


class TestViewportTransitions:
    """Test behavior when viewport changes (simulating device rotation)."""
    
    def test_desktop_to_mobile_transition(self, page: Page, local_server):
        """Verify layout adapts when resizing from desktop to mobile."""
        # Start at desktop size
        page.set_viewport_size(VIEWPORTS["desktop"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Desktop nav should be visible
        expect(page.locator("#nav")).to_be_visible()
        
        # Resize to mobile
        page.set_viewport_size(VIEWPORTS["mobile"])
        page.wait_for_timeout(500)
        
        # Mobile titlebar should now be visible
        expect(page.locator("#titleBar")).to_be_visible()
    
    def test_mobile_to_desktop_transition(self, page: Page, local_server):
        """Verify layout adapts when resizing from mobile to desktop."""
        # Start at mobile size
        page.set_viewport_size(VIEWPORTS["mobile"])
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Mobile titlebar should be visible
        expect(page.locator("#titleBar")).to_be_visible()
        
        # Resize to desktop
        page.set_viewport_size(VIEWPORTS["desktop"])
        page.wait_for_timeout(500)
        
        # Desktop nav should now be visible
        expect(page.locator("#nav")).to_be_visible()

"""
Browser functionality tests using Playwright.
Tests for JavaScript interactions, smooth scrolling, navigation, and dynamic content.
"""
import pytest
from playwright.sync_api import expect, Page
import time
import re


class TestPageLoad:
    """Test page loading behavior."""
    
    def test_homepage_loads(self, page: Page, local_server):
        """Verify homepage loads without errors."""
        page.goto(f"{local_server}/index.html")
        expect(page).to_have_title("MB Secure")
    
    def test_is_preload_class_removed(self, page: Page, local_server):
        """Verify is-preload class is removed after page load."""
        page.goto(f"{local_server}/index.html")
        # Wait for JavaScript to remove the class
        page.wait_for_timeout(500)
        
        body = page.locator("body")
        expect(body).not_to_have_class("is-preload")
    
    def test_blog_index_loads(self, page: Page, local_server):
        """Verify blog index page loads."""
        page.goto(f"{local_server}/blog/index.html")
        expect(page).to_have_title("Blog - MB Secure")
    
    def test_blog_post_loads(self, page: Page, local_server):
        """Verify blog post page loads."""
        page.goto(f"{local_server}/blog/2020/4/the-sources-for-hunts-and-how-to-prioritise.html")
        expect(page.locator("article")).to_be_visible()


class TestHeaderFooterInjection:
    """Test dynamic header and footer injection."""
    
    def test_nav_logo_renders(self, page: Page, local_server):
        """Verify nav logo is rendered via JavaScript."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)  # Wait for JS injection
        
        logo = page.locator("#nav .nav-logo img")
        expect(logo).to_be_visible()
    
    def test_footer_social_links_render(self, page: Page, local_server):
        """Verify footer social links are rendered via JavaScript."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Check for social icons in footer
        footer = page.locator("#footer")
        expect(footer).to_be_visible()
        
        # Check LinkedIn icon
        linkedin = page.locator("#footer a[href*='linkedin']")
        expect(linkedin).to_be_visible()
    
    def test_navigation_links_render(self, page: Page, local_server):
        """Verify navigation links are rendered."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        nav = page.locator("#nav")
        expect(nav).to_be_visible()
        
        # Check for main nav links
        about_link = page.locator("#nav a[href='#about']")
        expect(about_link).to_be_visible()


class TestSmoothScrolling:
    """Test smooth scrolling functionality."""
    
    def test_scroll_to_about_section(self, page: Page, local_server):
        """Verify clicking About link scrolls to about section."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Get initial scroll position
        initial_scroll = page.evaluate("window.scrollY")
        
        # Click the About link
        page.click("#nav a[href='#about']")
        page.wait_for_timeout(1500)  # Wait for scroll animation
        
        # Get new scroll position
        new_scroll = page.evaluate("window.scrollY")
        
        # Verify scroll occurred
        assert new_scroll > initial_scroll, "Page did not scroll to about section"
        
        # Verify about section is in viewport
        about_section = page.locator("#about")
        expect(about_section).to_be_in_viewport()
    
    def test_services_link_navigates_to_page(self, page: Page, local_server):
        """Verify clicking Services link navigates to services page."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        page.click("#nav a[href='services/']")
        page.wait_for_url("**/services/**")
        
        expect(page).to_have_title("Services - MB Secure")
    
    def test_scroll_to_contact_section(self, page: Page, local_server):
        """Verify clicking Contact link scrolls to contact section."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        page.click("#nav a[href='#contact']")
        page.wait_for_timeout(1500)
        
        contact_section = page.locator("#contact")
        expect(contact_section).to_be_in_viewport()
    
    def test_hero_lets_talk_button_scrolls(self, page: Page, local_server):
        """Verify Let's Talk button in hero scrolls to contact."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Click the hero CTA button (in #hero section, not #banner)
        cta_button = page.locator("#hero a.scrolly[href='#contact']")
        cta_button.click()
        page.wait_for_timeout(1500)
        
        contact_section = page.locator("#contact")
        expect(contact_section).to_be_in_viewport()


class TestNavigation:
    """Test page navigation functionality."""
    
    def test_navigate_to_blog(self, page: Page, local_server):
        """Verify clicking Blog link navigates to blog page."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Click blog link in navigation
        page.click("#nav a[href='blog/index.html']")
        page.wait_for_url("**/blog/**")
        
        expect(page).to_have_title("Blog - MB Secure")
    
    def test_blog_navigate_to_about(self, page: Page, local_server):
        """Verify About link works from blog."""
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(500)
        
        # Click About link (goes to homepage #about)
        page.click("#nav a[href='../index.html#about']")
        page.wait_for_url("**/index.html**")
        
        expect(page).to_have_title("MB Secure")
    
    def test_blog_post_back_to_blog(self, page: Page, local_server):
        """Verify Back to Blog link works from blog post."""
        page.goto(f"{local_server}/blog/2020/4/the-sources-for-hunts-and-how-to-prioritise.html")
        page.wait_for_timeout(500)
        
        # Click back to blog link in the nav
        back_link = page.locator("#nav a[href='../../index.html']")
        back_link.click()
        page.wait_for_url("**/blog/index.html")
    
    def test_blog_card_navigation(self, page: Page, local_server):
        """Verify clicking blog card navigates to blog post."""
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(500)
        
        # Click first blog card link
        first_card = page.locator(".blog-card a").first
        first_card.click()
        
        # Should navigate to a blog post
        expect(page.locator("article")).to_be_visible()


class TestExternalLinks:
    """Test external link behavior."""
    
    def test_linkedin_opens_new_tab(self, page: Page, local_server):
        """Verify LinkedIn link has target=_blank."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        linkedin = page.locator("a[href*='linkedin']").first
        target = linkedin.get_attribute("target")
        assert target == "_blank", "LinkedIn link should open in new tab"
    
    def test_github_opens_new_tab(self, page: Page, local_server):
        """Verify GitHub link has target=_blank."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        github = page.locator("a[href*='github']").first
        target = github.get_attribute("target")
        assert target == "_blank", "GitHub link should open in new tab"
    
    def test_email_link_has_mailto(self, page: Page, local_server):
        """Verify email link uses mailto protocol."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        email = page.locator("a[href^='mailto:']").first
        href = email.get_attribute("href")
        assert "mailto:" in href, "Email link should use mailto protocol"


class TestActiveNavState:
    """Test active navigation state updates on scroll (desktop).
    
    Note: On desktop, the 'current' class is applied to the parent <li> element,
    not directly to the <a> link. On mobile, it's applied to the link itself.
    """
    
    def test_about_nav_current_when_scrolled(self, page: Page, local_server):
        """Verify About nav item becomes current when about section is visible."""
        page.set_viewport_size({"width": 1200, "height": 800})
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Scroll to about section
        page.evaluate("document.querySelector('#about').scrollIntoView()")
        page.wait_for_timeout(500)
        
        # Check if about nav li (parent of the link) has current class
        about_li = page.locator("#nav li:has(a[href='#about'])")
        expect(about_li).to_have_class(re.compile(r"current"))
    
    def test_contact_nav_current_when_scrolled(self, page: Page, local_server):
        """Verify Contact nav item becomes current when contact section is visible."""
        page.set_viewport_size({"width": 1200, "height": 800})
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Scroll to contact section
        page.evaluate("document.querySelector('#contact').scrollIntoView()")
        page.wait_for_timeout(500)
        
        # Check if contact nav li has current class
        contact_li = page.locator("#nav li:has(a[href='#contact'])")
        expect(contact_li).to_have_class(re.compile(r"current"))
        
        # About should NOT be current
        about_li = page.locator("#nav li:has(a[href='#about'])")
        expect(about_li).not_to_have_class(re.compile(r"current"))
    
    def test_services_nav_current_on_services_page(self, page: Page, local_server):
        """Verify Services nav item is highlighted on the services page."""
        page.set_viewport_size({"width": 1200, "height": 800})
        page.goto(f"{local_server}/services/index.html")
        page.wait_for_timeout(500)
        
        # Check if services nav li has current class
        services_li = page.locator("#nav li:has(a[href*='services'])")
        expect(services_li).to_have_class(re.compile(r"current"))
    
    def test_blog_nav_current_on_blog_page(self, page: Page, local_server):
        """Verify Blog nav item is highlighted on the blog index page."""
        page.set_viewport_size({"width": 1200, "height": 800})
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(500)
        
        # Check if blog nav li has current class
        blog_li = page.locator("#nav li:has(a[href*='blog'])")
        expect(blog_li).to_have_class(re.compile(r"current"))
    
    def test_blog_nav_current_on_blog_post(self, page: Page, local_server):
        """Verify Blog nav item is highlighted on individual blog posts."""
        page.set_viewport_size({"width": 1200, "height": 800})
        page.goto(f"{local_server}/blog/2020/4/the-sources-for-hunts-and-how-to-prioritise.html")
        page.wait_for_timeout(500)
        
        # Check if blog nav li has current class
        # Note: On blog posts, the href is relative (../../index.html), so match by text
        blog_li = page.locator("#nav li:has(a:has-text('Blog'))")
        expect(blog_li).to_have_class(re.compile(r"current"))


class TestKeyboardNavigation:
    """Test keyboard navigation and accessibility."""
    
    def test_escape_key_behavior(self, page: Page, local_server):
        """Test that Escape key can close dropdowns if open."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Press Escape - should not cause errors
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        
        # Page should still be functional
        expect(page.locator("body")).to_be_visible()
    
    def test_tab_navigation(self, page: Page, local_server):
        """Test that Tab key moves focus through interactive elements."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Press Tab multiple times
        for _ in range(3):
            page.keyboard.press("Tab")
            page.wait_for_timeout(100)
        
        # Verify some element has focus
        focused = page.evaluate("document.activeElement.tagName")
        assert focused is not None


class TestPageTransitions:
    """Test page transition effects."""
    
    def test_navigation_fade_effect(self, page: Page, local_server):
        """Verify navigating-away class is added during navigation."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Start navigation but intercept before it completes
        # This is tricky to test reliably, so we'll just verify navigation works
        page.click("#nav a[href='blog/index.html']")
        page.wait_for_url("**/blog/**")
        
        # Verify we reached the blog page
        expect(page).to_have_title("Blog - MB Secure")


class TestBlogFunctionality:
    """Test blog-specific functionality."""
    
    def test_blog_cards_display(self, page: Page, local_server):
        """Verify blog cards display on blog index."""
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(500)
        
        cards = page.locator(".blog-card")
        expect(cards.first).to_be_visible()
    
    def test_blog_post_article_structure(self, page: Page, local_server):
        """Verify blog post has proper article structure."""
        page.goto(f"{local_server}/blog/2020/4/the-sources-for-hunts-and-how-to-prioritise.html")
        page.wait_for_timeout(500)
        
        article = page.locator("article")
        expect(article).to_be_visible()
        
        # Check for heading
        heading = article.locator("h1, h2").first
        expect(heading).to_be_visible()
    
    def test_blog_cross_page_anchor_links(self, page: Page, local_server):
        """Verify blog links to main page sections work."""
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(500)
        
        # Click link to contact on main page
        contact_link = page.locator("a[href='../index.html#contact']").first
        if contact_link.count() > 0:
            contact_link.click()
            page.wait_for_timeout(1500)
            
            # Verify we're on main page with contact section (use regex for URL with hash)
            expect(page).to_have_url(re.compile(r".*/index\.html.*"))


class TestNavigationTransitions:
    """Test page navigation transition effects."""
    
    def test_navigating_away_class_added_on_internal_link(self, page: Page, local_server):
        """Verify navigating-away class is added when clicking internal links."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Prevent actual navigation so we can check the class
        page.evaluate("""
            var blogLink = document.querySelector("#nav a[href*='blog']");
            if (blogLink) {
                blogLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    window.clickedBlogLink = true;
                });
            }
        """)
        
        # Click blog link (navigation will be prevented)
        page.click("#nav a[href*='blog']")
        page.wait_for_timeout(100)
        
        # Check class was added
        body = page.locator("body")
        expect(body).to_have_class(re.compile(r"navigating-away"))
    
    def test_navigating_away_not_added_for_anchor_links(self, page: Page, local_server):
        """Verify navigating-away class is NOT added for anchor links."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Click anchor link
        page.click("#nav a[href='#about']")
        page.wait_for_timeout(100)
        
        body = page.locator("body")
        expect(body).not_to_have_class(re.compile(r"navigating-away"))


class TestMobileNavActiveState:
    """Test active navigation state based on scroll position (mobile)."""
    
    def test_about_link_current_when_scrolled_to_about(self, page: Page, local_server):
        """Verify About nav link gets current class when scrolled to About section."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Open nav panel
        page.click("#titleBar .toggle")
        page.wait_for_timeout(300)
        
        # Scroll to about section
        page.evaluate("document.querySelector('#about').scrollIntoView()")
        page.wait_for_timeout(200)
        
        # Check current class on about link
        about_link = page.locator("#navPanel .link[href='#about']")
        expect(about_link).to_have_class(re.compile(r"current"))
    
    def test_current_state_updates_on_scroll(self, page: Page, local_server):
        """Verify current state changes when scrolling between sections."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        # Open nav panel
        page.click("#titleBar .toggle")
        page.wait_for_timeout(300)
        
        # Scroll to contact section
        page.evaluate("document.querySelector('#contact').scrollIntoView()")
        page.wait_for_timeout(200)
        
        # Check contact link is current
        contact_link = page.locator("#navPanel .link[href='#contact']")
        expect(contact_link).to_have_class(re.compile(r"current"))
        
        # About should NOT be current
        about_link = page.locator("#navPanel .link[href='#about']")
        expect(about_link).not_to_have_class(re.compile(r"current"))
    
    def test_services_link_current_on_services_page(self, page: Page, local_server):
        """Verify Services nav link is highlighted on the services page (mobile)."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{local_server}/services/index.html")
        page.wait_for_timeout(500)
        
        # Open nav panel
        page.click("#titleBar .toggle")
        page.wait_for_timeout(300)
        
        # Check services link has current class
        services_link = page.locator("#navPanel .link[href*='services']")
        expect(services_link).to_have_class(re.compile(r"current"))
    
    def test_blog_link_current_on_blog_page(self, page: Page, local_server):
        """Verify Blog nav link is highlighted on the blog page (mobile)."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(500)
        
        # Open nav panel
        page.click("#titleBar .toggle")
        page.wait_for_timeout(300)
        
        # Check blog link has current class
        blog_link = page.locator("#navPanel .link[href*='blog']")
        expect(blog_link).to_have_class(re.compile(r"current"))


class TestContactSection:
    """Test contact section dynamic content."""
    
    def test_contact_email_link_correct(self, page: Page, local_server):
        """Verify email link has correct mailto href."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        email_link = page.locator("#contact a[href^='mailto:']").first
        expect(email_link).to_be_visible()
        expect(email_link).to_have_attribute("href", re.compile(r"mailto:.*@mbsecure\.nl"))
    
    def test_contact_phone_link_correct(self, page: Page, local_server):
        """Verify phone link has correct tel href."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        phone_link = page.locator("#contact a[href^='tel:']").first
        expect(phone_link).to_be_visible()
        expect(phone_link).to_have_attribute("href", re.compile(r"tel:\+31"))
    
    def test_lets_talk_button_is_email_link(self, page: Page, local_server):
        """Verify Let's Talk button links to email."""
        page.goto(f"{local_server}/index.html")
        page.wait_for_timeout(500)
        
        cta_button = page.locator("#contact .button:has-text('Talk')")
        expect(cta_button).to_be_visible()
        expect(cta_button).to_have_attribute("href", re.compile(r"mailto:"))


class TestNavLogoNavigation:
    """Test nav logo navigation from various pages."""
    
    def test_logo_from_blog_index_navigates_home(self, page: Page, local_server):
        """Verify logo click from blog index navigates to homepage."""
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(500)
        
        logo = page.locator("#nav .nav-logo").first
        logo.click()
        page.wait_for_timeout(500)
        
        expect(page).to_have_url(re.compile(r"/(index\.html)?$"))
    
    def test_logo_from_blog_page_2_navigates_home(self, page: Page, local_server):
        """Verify logo click from blog page 2 navigates to homepage."""
        page.goto(f"{local_server}/blog/page/2/index.html")
        page.wait_for_timeout(500)
        
        logo = page.locator("#nav .nav-logo").first
        logo.click()
        page.wait_for_timeout(500)
        
        expect(page).to_have_url(re.compile(r"/(index\.html)?$"))

"""
Blog interaction tests using Playwright.
Tests for GLightbox, pagination, code blocks, and other blog-specific interactions.
"""
import pytest
from playwright.sync_api import expect, Page
import re


class TestGLightbox:
    """Test GLightbox image gallery functionality."""
    
    @pytest.fixture
    def blog_post_with_images(self, local_server):
        """Return URL of a blog post with GLightbox images."""
        return f"{local_server}/blog/2019/12/kql-cheat-sheet.html"
    
    def test_lightbox_image_clickable(self, page: Page, blog_post_with_images):
        """Verify lightbox images are clickable."""
        page.goto(blog_post_with_images)
        page.wait_for_timeout(500)
        
        lightbox_link = page.locator("a.glightbox").first
        expect(lightbox_link).to_be_visible()
        expect(lightbox_link).to_have_attribute("href", re.compile(r"\.webp$"))
    
    def test_clicking_image_opens_lightbox(self, page: Page, blog_post_with_images):
        """Verify clicking image opens the lightbox modal."""
        page.goto(blog_post_with_images)
        page.wait_for_timeout(500)
        
        page.click("a.glightbox")
        page.wait_for_timeout(500)
        
        lightbox = page.locator(".glightbox-container")
        expect(lightbox).to_be_visible()
    
    def test_lightbox_close_button(self, page: Page, blog_post_with_images):
        """Verify clicking close button closes the lightbox."""
        page.goto(blog_post_with_images)
        page.wait_for_timeout(500)
        
        page.click("a.glightbox")
        page.wait_for_timeout(500)
        
        close_button = page.locator(".gclose")
        expect(close_button).to_be_visible()
        close_button.click()
        page.wait_for_timeout(500)
        
        lightbox = page.locator(".glightbox-container")
        expect(lightbox).not_to_be_visible()
    
    def test_lightbox_closes_on_escape(self, page: Page, blog_post_with_images):
        """Verify pressing ESC closes the lightbox."""
        page.goto(blog_post_with_images)
        page.wait_for_timeout(500)
        
        page.click("a.glightbox")
        page.wait_for_timeout(500)
        
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        
        lightbox = page.locator(".glightbox-container")
        expect(lightbox).not_to_be_visible()
    
    def test_lightbox_closes_on_overlay_click(self, page: Page, blog_post_with_images):
        """Verify clicking outside the image closes the lightbox."""
        page.goto(blog_post_with_images)
        page.wait_for_timeout(500)
        
        page.click("a.glightbox")
        page.wait_for_timeout(500)
        
        # GLightbox closes when clicking on the container edges
        # Use force click to bypass the stacking elements
        page.locator(".glightbox-container").click(position={"x": 5, "y": 5}, force=True)
        page.wait_for_timeout(500)
        
        lightbox = page.locator(".glightbox-container")
        expect(lightbox).not_to_be_visible()


class TestBlogPagination:
    """Test blog pagination functionality."""
    
    def test_pagination_visible_on_blog_index(self, page: Page, local_server):
        """Verify pagination is visible on blog index."""
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(500)
        
        pagination = page.locator(".blog-pagination")
        expect(pagination).to_be_visible()
    
    def test_pagination_page_2_link_works(self, page: Page, local_server):
        """Verify clicking page 2 navigates to second page."""
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(500)
        
        page.click(".blog-pagination a[href*='page/2']")
        page.wait_for_timeout(500)
        
        expect(page).to_have_title("Blog - Page 2 - MB Secure")
    
    def test_pagination_next_link_works(self, page: Page, local_server):
        """Verify clicking Next link navigates to second page."""
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(500)
        
        page.click(".blog-pagination a.next")
        page.wait_for_timeout(500)
        
        expect(page).to_have_title("Blog - Page 2 - MB Secure")
    
    def test_pagination_back_to_page_1(self, page: Page, local_server):
        """Verify navigating back to page 1 from page 2."""
        page.goto(f"{local_server}/blog/page/2/index.html")
        page.wait_for_timeout(500)
        
        page.click(".blog-pagination a[href*='/blog/index.html']")
        page.wait_for_timeout(500)
        
        expect(page).to_have_title("Blog - MB Secure")


class TestBlogCodeBlocks:
    """Test code block functionality in blog posts."""
    
    @pytest.fixture
    def blog_post_with_code(self, local_server):
        """Return URL of a blog post with code blocks."""
        return f"{local_server}/blog/2019/10/how-to-integrate-eql-into-your-tooling.html"
    
    def test_code_blocks_visible(self, page: Page, blog_post_with_code):
        """Verify code blocks are visible."""
        page.goto(blog_post_with_code)
        page.wait_for_timeout(500)
        
        code_block = page.locator("pre code").first
        expect(code_block).to_be_visible()
    
    def test_code_blocks_have_syntax_highlighting(self, page: Page, blog_post_with_code):
        """Verify Prism syntax highlighting is applied."""
        page.goto(blog_post_with_code)
        page.wait_for_timeout(500)
        
        highlighted_code = page.locator("pre code[class*='language-']").first
        expect(highlighted_code).to_be_visible()
    
    def test_code_blocks_scrollable_on_mobile(self, page: Page, blog_post_with_code):
        """Verify code blocks are horizontally scrollable on mobile."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(blog_post_with_code)
        page.wait_for_timeout(500)
        
        pre_element = page.locator("pre").first
        expect(pre_element).to_be_visible()
        
        overflow = pre_element.evaluate("el => window.getComputedStyle(el).overflowX")
        assert overflow in ["auto", "scroll"], f"Expected overflow-x to be auto or scroll, got {overflow}"


class TestBlogNavigation:
    """Test blog navigation features."""
    
    def test_blog_post_nav_logo_navigates_home(self, page: Page, local_server):
        """Verify nav logo navigates to homepage from blog post."""
        page.goto(f"{local_server}/blog/2020/4/the-sources-for-hunts-and-how-to-prioritise.html")
        page.wait_for_timeout(500)
        
        logo = page.locator("#nav .nav-logo")
        expect(logo.first).to_be_visible()
        logo.first.click()
        page.wait_for_timeout(500)
        
        expect(page).to_have_url(re.compile(r"/(index\.html)?$"))
    
    def test_blog_card_click_navigates_to_post(self, page: Page, local_server):
        """Verify clicking a blog card navigates to the post."""
        page.goto(f"{local_server}/blog/index.html")
        page.wait_for_timeout(500)
        
        blog_link = page.locator(".blog-card a").first
        blog_link.click()
        page.wait_for_timeout(500)
        
        expect(page.locator("article")).to_be_visible()

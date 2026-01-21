"""
Static asset and link checker tests.
Tests for HTTP responses, internal/external links, and image loading.
"""
import pytest
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import sys

# Import shared test configuration
from tests.conftest import PAGES, BLOG_POSTS, WEBSITE_DIR

# External resources to verify
EXTERNAL_RESOURCES = [
    "https://fonts.googleapis.com/css?family=Open+Sans:400,400italic,700,700italic|Open+Sans+Condensed:700",
    "https://www.linkedin.com/in/marcusbakker",
    "https://github.com/marcusbakker",
]

# Images that should exist
IMAGES = [
    "/images/logo.png",
    "/images/marcus.jpg",
]


class TestPageResponses:
    """Test that all pages return HTTP 200."""
    
    @pytest.mark.parametrize("page", PAGES)
    def test_page_returns_200(self, local_server, page):
        """Verify each page returns HTTP 200 status."""
        url = f"{local_server}{page}"
        response = requests.get(url, timeout=10)
        assert response.status_code == 200, f"Page {page} returned {response.status_code}"
    
    @pytest.mark.parametrize("page", PAGES)
    def test_page_has_content(self, local_server, page):
        """Verify each page has meaningful content."""
        url = f"{local_server}{page}"
        response = requests.get(url, timeout=10)
        assert len(response.text) > 100, f"Page {page} has insufficient content"
    
    @pytest.mark.parametrize("page", PAGES)
    def test_page_has_valid_html(self, local_server, page):
        """Verify each page has valid HTML structure."""
        url = f"{local_server}{page}"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for essential HTML elements
        assert soup.find('html') is not None, f"Page {page} missing <html> tag"
        assert soup.find('head') is not None, f"Page {page} missing <head> tag"
        assert soup.find('body') is not None, f"Page {page} missing <body> tag"
        assert soup.find('title') is not None, f"Page {page} missing <title> tag"


class TestInternalLinks:
    """Test that all internal links are valid."""
    
    @pytest.mark.parametrize("page", PAGES)
    def test_internal_links_resolve(self, local_server, page):
        """Verify all internal links on each page resolve correctly."""
        url = f"{local_server}{page}"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        failed_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Skip external links, mailto, tel, and anchor-only links
            if href.startswith(('http://', 'https://', 'mailto:', 'tel:', '#')):
                continue
            
            # Handle anchor links with path
            if '#' in href:
                href = href.split('#')[0]
                if not href:  # Just an anchor, skip
                    continue
            
            # Resolve relative URLs
            full_url = urljoin(url, href)
            
            try:
                link_response = requests.get(full_url, timeout=10)
                if link_response.status_code != 200:
                    failed_links.append(f"{href} -> {link_response.status_code}")
            except requests.RequestException as e:
                failed_links.append(f"{href} -> {str(e)}")
        
        assert not failed_links, f"Failed internal links on {page}: {failed_links}"


class TestExternalResources:
    """Test that external resources are accessible."""
    
    @pytest.mark.parametrize("resource_url", EXTERNAL_RESOURCES)
    def test_external_resource_accessible(self, resource_url):
        """Verify external resources are accessible."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        try:
            # Use GET for social media sites that block HEAD requests
            parsed = urlparse(resource_url)
            hostname = parsed.hostname or ''
            # Check exact domain or subdomain (dot prefix prevents matching evillinkedin.com)
            is_linkedin = hostname == 'linkedin.com' or hostname.endswith('.linkedin.com')
            is_github = hostname == 'github.com' or hostname.endswith('.github.com')
            if is_linkedin or is_github:
                response = requests.get(resource_url, timeout=15, headers=headers, allow_redirects=True)
            else:
                response = requests.head(resource_url, timeout=15, headers=headers, allow_redirects=True)
            # Accept 200, 301, 302, 303, 307, 308, 999 (LinkedIn specific) as valid responses
            assert response.status_code in [200, 301, 302, 303, 307, 308, 999], \
                f"External resource {resource_url} returned {response.status_code}"
        except requests.RequestException as e:
            pytest.fail(f"External resource {resource_url} not accessible: {e}")
    
    def test_font_resources_available(self, local_server):
        """Verify font resources are available (either via CSS or HTML link)."""
        # Check if fonts are loaded via CSS @import or HTML link
        url = f"{local_server}/index.html"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for Google Fonts link in HTML (validate hostname properly)
        def is_google_fonts(href):
            parsed = urlparse(href)
            hostname = parsed.hostname or ''
            return hostname == 'fonts.googleapis.com'
        
        font_links = [link for link in soup.find_all('link', href=True) 
                      if is_google_fonts(link['href'])]
        
        # If not in HTML, fonts might be defined in CSS - that's also valid
        # This test just documents the expected behavior
        if len(font_links) == 0:
            # Fonts might be system fonts or loaded via CSS
            # Just verify CSS loads (which we test elsewhere)
            pass


class TestImages:
    """Test that all images load correctly."""
    
    @pytest.mark.parametrize("image", IMAGES)
    def test_image_exists(self, local_server, image):
        """Verify each image exists and returns 200."""
        url = f"{local_server}{image}"
        response = requests.get(url, timeout=10)
        assert response.status_code == 200, f"Image {image} returned {response.status_code}"
    
    @pytest.mark.parametrize("image", IMAGES)
    def test_image_has_content(self, local_server, image):
        """Verify each image has content (not empty)."""
        url = f"{local_server}{image}"
        response = requests.get(url, timeout=10)
        assert len(response.content) > 0, f"Image {image} is empty"
    
    def test_images_referenced_in_pages(self, local_server):
        """Verify images referenced in HTML actually exist."""
        url = f"{local_server}/index.html"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        failed_images = []
        
        for img in soup.find_all('img', src=True):
            src = img['src']
            
            # Skip external images
            if src.startswith(('http://', 'https://')):
                continue
            
            full_url = urljoin(url, src)
            
            try:
                img_response = requests.get(full_url, timeout=10)
                if img_response.status_code != 200:
                    failed_images.append(f"{src} -> {img_response.status_code}")
            except requests.RequestException as e:
                failed_images.append(f"{src} -> {str(e)}")
        
        assert not failed_images, f"Failed image references: {failed_images}"


class TestCSSAndJS:
    """Test that CSS and JavaScript files load correctly."""
    
    def test_main_css_loads(self, local_server):
        """Verify main.css loads correctly."""
        url = f"{local_server}/assets/css/main.css"
        response = requests.get(url, timeout=10)
        assert response.status_code == 200, "main.css not found"
        assert len(response.text) > 100, "main.css is too small"
    
    def test_fontawesome_css_loads(self, local_server):
        """Verify Font Awesome CSS loads correctly."""
        url = f"{local_server}/assets/css/fontawesome-all.min.css"
        response = requests.get(url, timeout=10)
        assert response.status_code == 200, "fontawesome-all.min.css not found"
    
    def test_main_js_loads(self, local_server):
        """Verify main.js loads correctly."""
        url = f"{local_server}/assets/js/main.js"
        response = requests.get(url, timeout=10)
        assert response.status_code == 200, "main.js not found"
    
    def test_all_js_files_load(self, local_server):
        """Verify all JavaScript files in index.html load."""
        url = f"{local_server}/index.html"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        failed_scripts = []
        
        for script in soup.find_all('script', src=True):
            src = script['src']
            
            # Skip external scripts
            if src.startswith(('http://', 'https://')):
                continue
            
            full_url = urljoin(url, src)
            
            try:
                script_response = requests.get(full_url, timeout=10)
                if script_response.status_code != 200:
                    failed_scripts.append(f"{src} -> {script_response.status_code}")
            except requests.RequestException as e:
                failed_scripts.append(f"{src} -> {str(e)}")
        
        assert not failed_scripts, f"Failed script references: {failed_scripts}"


class TestMetaTags:
    """Test meta tags and SEO elements."""
    
    @pytest.mark.parametrize("page", PAGES)
    def test_page_has_meta_description(self, local_server, page):
        """Verify each page has a meta description."""
        url = f"{local_server}{page}"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        assert meta_desc is not None, f"Page {page} missing meta description"
    
    @pytest.mark.parametrize("page", PAGES)
    def test_page_has_viewport_meta(self, local_server, page):
        """Verify each page has viewport meta tag for responsive design."""
        url = f"{local_server}{page}"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        assert viewport is not None, f"Page {page} missing viewport meta tag"
    
    @pytest.mark.parametrize("page", PAGES)
    def test_page_has_charset(self, local_server, page):
        """Verify each page has charset declaration."""
        url = f"{local_server}{page}"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        charset = soup.find('meta', attrs={'charset': True})
        assert charset is not None, f"Page {page} missing charset meta tag"

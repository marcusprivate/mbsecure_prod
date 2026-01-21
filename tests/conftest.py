"""
Pytest configuration and fixtures for MB Secure website tests.
"""
import pytest
import threading
import http.server
import socketserver
import os
import time
from pathlib import Path


# Base directory for the website
WEBSITE_DIR = Path(__file__).parent.parent
BASE_URL = "http://localhost:8000"

def discover_blog_posts():
    """Dynamically discover all blog post HTML files."""
    blog_dir = WEBSITE_DIR / "blog"
    posts = []
    for html_file in blog_dir.glob("**/*.html"):
        # Skip index files
        if html_file.name == "index.html":
            continue
        # Convert to URL path relative to website root
        relative_path = html_file.relative_to(WEBSITE_DIR)
        posts.append(f"/{relative_path}")
    return sorted(posts)


# All discovered blog posts
BLOG_POSTS = discover_blog_posts()

class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that suppresses logging output."""
    
    def log_message(self, format, *args):
        pass  # Suppress logging
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEBSITE_DIR), **kwargs)


class ReusableTCPServer(socketserver.TCPServer):
    """TCP server that allows address reuse."""
    allow_reuse_address = True


@pytest.fixture(scope="session")
def local_server():
    """Start a local HTTP server for the website."""
    server = ReusableTCPServer(("", 8000), QuietHTTPHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)  # Give server time to start
    yield BASE_URL
    server.shutdown()


def pytest_configure(config):
    """Skip WebKit tests - known flakiness with Playwright on macOS."""
    config.addinivalue_line(
        "markers", "skip_webkit: mark test to skip on webkit"
    )


def pytest_collection_modifyitems(config, items):
    """Skip WebKit tests and skip visual tests for non-Chromium browsers."""
    skip_webkit = pytest.mark.skip(reason="WebKit has known flakiness issues")
    skip_visual_firefox = pytest.mark.skip(reason="Visual tests use Chromium baselines only")
    
    for item in items:
        if "webkit" in item.nodeid:
            item.add_marker(skip_webkit)
        # Skip visual tests for Firefox (baselines are Chromium-only)
        elif "firefox" in item.nodeid and "test_visual" in item.nodeid:
            item.add_marker(skip_visual_firefox)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context with viewport and other settings."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def base_url(local_server):
    """Provide the base URL for tests."""
    return local_server


# List of all pages to test (includes all dynamically discovered blog posts)
PAGES = [
    "/index.html",
    "/services/index.html",
    "/blog/index.html",
    "/blog/page/2/index.html",
] + BLOG_POSTS

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

/**
 * Navigation Component
 * 
 * Injects the site navigation with integrated logo based on the current page type.
 * Uses MBSecure namespace from site-config.js.
 * 
 * NOTE: This script runs immediately (not on DOMContentLoaded) because:
 * - The nav element exists in the HTML
 * - main.js needs the nav content populated before it builds the mobile nav panel
 * - This script must be loaded BEFORE main.js
 */
(function() {
    'use strict';

    // Inject skip-to-content link for accessibility (keyboard users)
    var skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-to-content';
    skipLink.textContent = 'Skip to main content';
    document.body.insertBefore(skipLink, document.body.firstChild);

    // Run immediately since nav element exists and main.js needs it populated
    var navElement = document.getElementById("nav");
    
    if (!navElement) {
        return; // No nav placeholder on this page
    }

    // Use MBSecure namespace with fallback to legacy globals
    var getBasePathFn = (typeof MBSecure !== 'undefined') ? MBSecure.getBasePath : 
                        (typeof getBasePath === 'function') ? getBasePath : function() { return ''; };
    var basePath = getBasePathFn();

    // Get config for logo
    var config = (typeof MBSecure !== 'undefined') ? MBSecure.config : 
                 (typeof SITE_CONFIG !== 'undefined') ? SITE_CONFIG : null;

    // Determine page type based on URL and body class
    var isHomepage = document.body.classList.contains('homepage');
    var isBlogPost = document.body.classList.contains('blog-post-page');
    var isBlogIndex = document.body.classList.contains('blog-index-page');
    var isServicesPage = document.body.classList.contains('services-page');

    // Calculate paths
    var homeLink = basePath ? basePath + 'index.html' : 'index.html';
    var logoSrc = basePath + 'images/logo.png';
    var logoAlt = config && config.branding ? config.branding.logoAlt : 'MB Secure Logo';

    // Calculate blog index path for blog posts (go up to blog/ folder)
    var blogIndexPath = basePath + 'blog/index.html';
    if (isBlogPost) {
        // Blog posts are at /blog/YYYY/MM/post.html, so need to go up 2 levels
        blogIndexPath = '../../index.html';
    } else if (isBlogIndex && basePath !== '../') {
        // Nested blog index pages (like /blog/page/2/)
        blogIndexPath = basePath + 'blog/index.html';
    }

    // Build logo HTML
    var logoHTML = 
        '<a href="' + homeLink + '" class="nav-logo">' +
            '<img src="' + logoSrc + '" alt="' + logoAlt + '" />' +
        '</a>';

    // Helper to build nav link item
    function navItem(href, label, isCurrent, scrolly) {
        var liClass = isCurrent ? ' class="current"' : '';
        var aClass = scrolly ? ' class="scrolly"' : '';
        return '<li' + liClass + '><a href="' + href + '"' + aClass + '>' + label + '</a></li>';
    }

    // Determine which section is current
    var currentPage = isServicesPage ? 'services' : (isBlogIndex || isBlogPost) ? 'blog' : null;

    // Build nav links based on page type
    var navLinksHTML;
    if (isHomepage) {
        // Homepage uses scrolly anchor links
        navLinksHTML = '<ul>' +
            navItem('#about', 'About', false, true) +
            navItem('services/', 'Services', false, false) +
            navItem('#contact', 'Contact', false, true) +
            navItem('blog/index.html', 'Blog', false, false) +
            '</ul>';
    } else {
        // All other pages use absolute paths back to homepage
        navLinksHTML = '<ul>' +
            navItem(basePath + 'index.html#about', 'About', false, false) +
            navItem(basePath + 'services/', 'Services', currentPage === 'services', false) +
            navItem(basePath + 'index.html#contact', 'Contact', false, false) +
            navItem(blogIndexPath, 'Blog', currentPage === 'blog', false) +
            '</ul>';
    }

    // Wrap in container with logo + nav links
    var navHTML = 
        '<div class="nav-container">' +
            logoHTML +
            '<div class="nav-links">' + navLinksHTML + '</div>' +
        '</div>';

    navElement.innerHTML = navHTML;

    // Mark current page in mobile menu for non-homepage pages
    if (!isHomepage) {
        document.addEventListener('DOMContentLoaded', function() {
            var navPanel = document.getElementById('navPanel');
            if (!navPanel) return;

            var mobileLinks = navPanel.querySelectorAll('.link');

            if (isBlogIndex || isBlogPost) {
                mobileLinks.forEach(function(link) {
                    if (link.getAttribute('href').indexOf('blog') !== -1) {
                        link.classList.add('current');
                    }
                });
            } else if (isServicesPage) {
                mobileLinks.forEach(function(link) {
                    if (link.getAttribute('href').indexOf('services') !== -1) {
                        link.classList.add('current');
                    }
                });
            }
        });
    }

    // Scroll spy for homepage - highlight current section in nav and mobile menu
    if (isHomepage) {
        document.addEventListener('DOMContentLoaded', function() {
            var sections = document.querySelectorAll('section[id]');
            var navLinks = navElement.querySelectorAll('a.scrolly');
            
            if (!sections.length || !navLinks.length) return;

            var currentSection = null;

            function updateCurrentSection(id) {
                if (currentSection === id) return;
                currentSection = id;

                // Remove current from all nav items (desktop)
                navLinks.forEach(function(link) {
                    link.parentElement.classList.remove('current');
                });
                
                // Add current to matching nav item (desktop)
                if (id) {
                    var activeLink = navElement.querySelector('a[href="#' + id + '"]');
                    if (activeLink) {
                        activeLink.parentElement.classList.add('current');
                    }
                }

                // Also update mobile nav panel if it exists
                var navPanel = document.getElementById('navPanel');
                if (navPanel) {
                    var mobileLinks = navPanel.querySelectorAll('.link');
                    mobileLinks.forEach(function(link) {
                        link.classList.remove('current');
                    });
                    if (id) {
                        var activeMobileLink = navPanel.querySelector('.link[href="#' + id + '"]');
                        if (activeMobileLink) {
                            activeMobileLink.classList.add('current');
                        }
                    }
                }
            }

            function onScroll() {
                var scrollPos = window.scrollY + window.innerHeight * 0.3;
                var foundSection = null;

                sections.forEach(function(section) {
                    var top = section.offsetTop;
                    var bottom = top + section.offsetHeight;
                    
                    if (scrollPos >= top && scrollPos < bottom) {
                        foundSection = section.getAttribute('id');
                    }
                });

                updateCurrentSection(foundSection);
            }

            window.addEventListener('scroll', onScroll, { passive: true });
            onScroll(); // Initial check
        });
    }
})();

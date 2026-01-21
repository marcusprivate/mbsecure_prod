/**
 * MB Secure Site Configuration
 * 
 * Centralized configuration for contact info, social links, and branding.
 * Update values here to change them across the entire website.
 */
(function(global) {
    'use strict';

    var SITE_CONFIG = {
        // Contact Information
        contact: {
            email: "Marcus@MBSecure.nl",
            phone: "+31 6 41 54 50 71"
        },

        // Social Media Links
        social: {
            linkedin: "https://www.linkedin.com/in/marcusbakker",
            github: "https://github.com/marcusbakker",
            x: "https://x.com/Bakk3rM"
        },

        // Branding
        branding: {
            siteName: "MB Secure",
            logoAlt: "MB Secure"
        }
    };

    /**
     * Utility: Get the base path for assets based on current page location.
     * Builds a relative prefix (../) based on path depth so nested blog pages resolve correctly.
     * Handles GitHub Pages project sites (e.g., username.github.io/project-name/)
     */
    function getBasePath() {
        var path = window.location.pathname;
        var segments = path.split('/').filter(Boolean); // ignore leading/trailing slashes

        // Detect GitHub Pages project site (username.github.io/project-name/)
        // The project folder should not count toward the depth calculation
        var isGitHubProjectSite = window.location.hostname.endsWith('.github.io') && 
                                   segments.length > 0 && 
                                   segments[0] !== 'index.html';
        
        // Remove the project folder from segments if on GitHub Pages project site
        if (isGitHubProjectSite) {
            segments = segments.slice(1);
        }

        // Check if we're in a directory (path ends with / but not root)
        // e.g., /blog/ has segments ['blog'] but needs '../' prefix
        var isInDirectory = path.endsWith('/') && path !== '/';
        
        // Root pages ("/" or "/index.html") need no prefix
        if (segments.length === 0 || (segments.length === 1 && !isInDirectory)) {
            return '';
        }

        // For directory paths like /blog/, depth equals segment count
        // For file paths like /blog/index.html, depth is segment count - 1
        var depth = isInDirectory ? segments.length : segments.length - 1;
        return Array(depth).fill('..').join('/') + '/';
    }

    /**
     * Utility: Throttle function execution for performance
     */
    function throttle(func, limit) {
        var inThrottle;
        return function() {
            var args = arguments;
            var context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(function() { inThrottle = false; }, limit);
            }
        };
    }

    // Expose to global scope via MBSecure namespace
    global.MBSecure = {
        config: SITE_CONFIG,
        getBasePath: getBasePath,
        throttle: throttle
    };

})(window);

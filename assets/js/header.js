/**
 * Header Component
 * Injects the site header. Uses MBSecure namespace from site-config.js.
 */
(function() {
    'use strict';

    document.addEventListener("DOMContentLoaded", function() {
        // Use MBSecure namespace with fallback to legacy globals
        var config = (typeof MBSecure !== 'undefined') ? MBSecure.config : 
                     (typeof SITE_CONFIG !== 'undefined') ? SITE_CONFIG : null;
        var getBasePath = (typeof MBSecure !== 'undefined') ? MBSecure.getBasePath : 
                          window.getBasePath;

        if (!config || typeof getBasePath !== 'function') {
            console.error('Header: MBSecure namespace not available');
            return;
        }

        var basePath = getBasePath();
        var homeLink = basePath ? basePath + 'index.html' : 'index.html';
        var logoSrc = basePath + 'images/logo.png';

        var headerHTML = 
            '<div class="logo container">' +
                '<div>' +
                    '<h1><a href="' + homeLink + '" id="logo">' +
                        '<img src="' + logoSrc + '" alt="' + config.branding.logoAlt + '" class="logo-img" />' +
                    '</a></h1>' +
                '</div>' +
            '</div>';

        var headerElement = document.getElementById("header");
        if (headerElement) {
            headerElement.innerHTML = headerHTML;
        }
    });
})();

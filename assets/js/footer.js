/**
 * Footer Component
 * Injects the site footer with social links. Uses MBSecure namespace from site-config.js.
 */
(function() {
    'use strict';

    document.addEventListener("DOMContentLoaded", function() {
        // Use MBSecure namespace with fallback to legacy globals
        var config = (typeof MBSecure !== 'undefined') ? MBSecure.config : 
                     (typeof SITE_CONFIG !== 'undefined') ? SITE_CONFIG : null;

        if (!config) {
            console.error('Footer: MBSecure namespace not available');
            return;
        }

        var footerHTML = 
            '<div class="container">' +
                '<div class="row gtr-200">' +
                    '<div class="col-12">' +
                        '<section>' +
                            '<ul class="contact">' +
                                '<li><a class="icon brands fa-linkedin-in" href="' + config.social.linkedin + '" target="_blank" rel="noopener noreferrer" aria-label="Connect on LinkedIn"><span class="label">LinkedIn</span></a></li>' +
                                '<li><a class="icon fa-x-logo" href="' + config.social.x + '" target="_blank" rel="noopener noreferrer" aria-label="View X profile"><span class="label">X</span></a></li>' +
                                '<li><a class="icon brands fa-github" href="' + config.social.github + '" target="_blank" rel="noopener noreferrer" aria-label="View GitHub profile"><span class="label">GitHub</span></a></li>' +
                                '<li><a class="icon solid fa-envelope" href="mailto:' + config.contact.email + '" aria-label="Send email"><span class="label">Email</span></a></li>' +
                            '</ul>' +
                        '</section>' +
                    '</div>' +
                '</div>' +
            '</div>';

        var footerElement = document.getElementById("footer");
        if (footerElement) {
            footerElement.innerHTML = footerHTML;
        }
    });
})();
/**
 * Blog Post Initialization
 * 
 * Initializes shared blog functionality:
 * - GLightbox for image galleries
 * - Prism line numbers plugin
 * - Any other blog-specific features
 * 
 * Include this script on all blog post pages to avoid inline <script> tags.
 */
(function() {
    'use strict';

    document.addEventListener("DOMContentLoaded", function() {
        // Initialize GLightbox if available and there are lightbox elements
        if (typeof GLightbox !== 'undefined') {
            var lightboxElements = document.querySelectorAll('.glightbox');
            if (lightboxElements.length > 0) {
                GLightbox({
                    selector: '.glightbox',
                    touchNavigation: true,
                    closeButton: true,
                    svg: {
                        close: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>'
                    }
                });
            }
        }

        // Prism line numbers are auto-initialized via the plugin
        // No explicit initialization needed

        // Remove is-preload class after page load
        setTimeout(function() {
            document.body.classList.remove('is-preload');
        }, 100);
    });
})();

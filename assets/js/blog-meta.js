/**
 * Blog Meta / Structured Data Generator
 * 
 * Dynamically generates JSON-LD structured data for blog posts from data attributes.
 * This centralizes the structured data configuration so it can be updated easily.
 * 
 * Usage: Add data attributes to the article element:
 *   data-headline="Post Title"
 *   data-date-published="2019-12-10"
 *   data-date-modified="2020-02-03"
 *   data-description="Post description"
 *   data-image="https://mbsecure.nl/images/blog/image.png" (optional)
 */
(function() {
    'use strict';

    document.addEventListener("DOMContentLoaded", function() {
        var article = document.querySelector('article.blog-post');
        
        if (!article) {
            return; // Not a blog post page
        }

        // Check if structured data placeholder exists
        var metaPlaceholder = document.getElementById('blog-structured-data');
        if (!metaPlaceholder) {
            return; // No placeholder for structured data injection
        }

        // Get data attributes
        var headline = article.dataset.headline;
        var datePublished = article.dataset.datePublished;
        var dateModified = article.dataset.dateModified || datePublished;
        var description = article.dataset.description;
        var image = article.dataset.image;

        // Skip if required data is missing
        if (!headline || !datePublished) {
            console.warn('BlogMeta: Missing required data attributes (headline, datePublished)');
            return;
        }

        // Use MBSecure namespace with fallback
        var config = (typeof MBSecure !== 'undefined') ? MBSecure.config : 
                     (typeof SITE_CONFIG !== 'undefined') ? SITE_CONFIG : {};
        
        var authorUrl = config.social ? config.social.linkedin : 'https://www.linkedin.com/in/marcusbakker';

        // Build structured data object
        var structuredData = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": headline,
            "datePublished": datePublished,
            "dateModified": dateModified,
            "author": {
                "@type": "Person",
                "name": "Marcus Bakker",
                "url": authorUrl
            },
            "publisher": {
                "@type": "Organization",
                "name": "MB Secure",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://mbsecure.nl/images/logo.png"
                }
            },
            "description": description || ""
        };

        // Add image if provided
        if (image) {
            structuredData.image = image;
        }

        // Create and inject the script element
        var script = document.createElement('script');
        script.type = 'application/ld+json';
        script.textContent = JSON.stringify(structuredData, null, '\t');
        
        metaPlaceholder.appendChild(script);
    });
})();

/**
 * Contact Section Injection
 * 
 * Dynamically injects contact information from MBSecure namespace.
 * This centralizes contact info so it can be updated in one place.
 */
(function() {
    'use strict';

    document.addEventListener("DOMContentLoaded", function() {
        var contactElement = document.getElementById("contact-content");
        
        if (!contactElement) {
            return; // No contact placeholder on this page
        }

        // Use MBSecure namespace with fallback to legacy globals
        var config = (typeof MBSecure !== 'undefined') ? MBSecure.config : 
                     (typeof SITE_CONFIG !== 'undefined') ? SITE_CONFIG : {};
        var contact = config.contact || {};
        var email = (contact.email || 'marcus@mbsecure.nl').toLowerCase();
        var phone = contact.phone || '+31 6 41 54 50 71';
        
        // Format phone for tel: link (remove spaces)
        var phoneLink = phone.replace(/\s/g, '');

        var contactHTML = 
            '<div class="contact-info">' +
                '<div class="contact-item">' +
                    '<a href="mailto:' + email + '" class="contact-icon-link" aria-label="Send email">' +
                        '<i class="fas fa-envelope"></i>' +
                    '</a>' +
                    '<div>' +
                        '<strong>Email</strong>' +
                        '<a href="mailto:' + email + '">' + email + '</a>' +
                    '</div>' +
                '</div>' +
                '<div class="contact-item">' +
                    '<a href="tel:' + phoneLink + '" class="contact-icon-link" aria-label="Call phone">' +
                        '<i class="fas fa-phone"></i>' +
                    '</a>' +
                    '<div>' +
                        '<strong>Phone</strong>' +
                        '<a href="tel:' + phoneLink + '">' + phone + '</a>' +
                    '</div>' +
                '</div>' +
            '</div>' +
            '<div class="contact-cta">' +
                '<a href="mailto:' + email + '" class="button primary large">Let\'s Talk</a>' +
            '</div>';

        contactElement.innerHTML = contactHTML;
    });
})();

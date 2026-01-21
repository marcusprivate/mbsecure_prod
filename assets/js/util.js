/**
 * Utility functions for MB Secure website (vanilla JS)
 */
(function() {
	'use strict';

	/**
	 * Escape HTML special characters to prevent XSS
	 * @param {string} str - The string to escape
	 * @return {string} Escaped string safe for HTML insertion
	 */
	function escapeHtml(str) {
		if (!str) return '';
		return String(str)
			.replace(/&/g, '&amp;')
			.replace(/</g, '&lt;')
			.replace(/>/g, '&gt;')
			.replace(/"/g, '&quot;')
			.replace(/'/g, '&#39;');
	}

	/**
	 * Generate an indented list of links from a nav element.
	 * @param {HTMLElement} nav - The navigation element to process
	 * @return {string} HTML string of links
	 */
	function navList(nav) {
		var links = nav.querySelectorAll('a');
		var result = [];

		links.forEach(function(link) {
			// Count parent li elements to determine depth
			var indent = 0;
			var parent = link.parentElement;
			while (parent && parent !== nav) {
				if (parent.tagName === 'LI') indent++;
				parent = parent.parentElement;
			}
			indent = Math.max(0, indent - 1);

			var href = link.getAttribute('href') || '';
			var target = link.getAttribute('target') || '';

			result.push(
				'<a ' +
					'class="link depth-' + indent + '"' +
					(target ? ' target="' + escapeHtml(target) + '"' : '') +
					(href ? ' href="' + escapeHtml(href) + '"' : '') +
				'>' +
					'<span class="indent-' + indent + '"></span>' +
					escapeHtml(link.textContent) +
				'</a>'
			);
		});

		return result.join('');
	}

	/**
	 * Panel-ify an element (slide-in panel with touch support)
	 * @param {HTMLElement} element - The panel element
	 * @param {object} userConfig - Configuration options
	 */
	function panel(element, userConfig) {
		if (!element) return;

		var id = element.id;
		var body = document.body;

		// Default config
		var config = Object.assign({
			delay: 0,
			hideOnClick: false,
			hideOnEscape: false,
			hideOnSwipe: false,
			resetScroll: false,
			resetForms: false,
			side: null,
			target: element,
			visibleClass: 'visible'
		}, userConfig);

		// Ensure target is an element
		if (typeof config.target === 'string') {
			config.target = document.querySelector(config.target);
		}

		// Touch tracking
		var touchPosX = null;
		var touchPosY = null;

		// Hide method
		function hide(event) {
			if (!config.target.classList.contains(config.visibleClass)) {
				return;
			}

			if (event) {
				event.preventDefault();
				event.stopPropagation();
			}

			config.target.classList.remove(config.visibleClass);

			setTimeout(function() {
				if (config.resetScroll) {
					element.scrollTop = 0;
				}
				if (config.resetForms) {
					element.querySelectorAll('form').forEach(function(form) {
						form.reset();
					});
				}
			}, config.delay);
		}

		// Expose hide method on element
		element._hide = hide;

		// Hide on click (for links inside panel)
		if (config.hideOnClick) {
			element.querySelectorAll('a').forEach(function(link) {
				link.style.webkitTapHighlightColor = 'rgba(0,0,0,0)';
			});

			element.addEventListener('click', function(event) {
				var link = event.target.closest('a');
				if (!link) return;

				var href = link.getAttribute('href');
				var target = link.getAttribute('target');

				if (!href || href === '#' || href === '' || href === '#' + id) {
					return;
				}

				event.preventDefault();
				event.stopPropagation();

				if (target === '_blank') {
					window.open(href);
				} else {
					window.location.href = href;
				}
			});
		}

		// Touch events
		element.addEventListener('touchstart', function(event) {
			touchPosX = event.touches[0].pageX;
			touchPosY = event.touches[0].pageY;
		});

		element.addEventListener('touchmove', function(event) {
			if (touchPosX === null || touchPosY === null) return;

			var diffX = touchPosX - event.touches[0].pageX;
			var diffY = touchPosY - event.touches[0].pageY;
			var th = element.offsetHeight;
			var ts = element.scrollHeight - element.scrollTop;

			// Hide on swipe
			if (config.hideOnSwipe) {
				var result = false;
				var boundary = 20;
				var delta = 50;

				switch (config.side) {
					case 'left':
						result = (diffY < boundary && diffY > -boundary) && (diffX > delta);
						break;
					case 'right':
						result = (diffY < boundary && diffY > -boundary) && (diffX < -delta);
						break;
					case 'top':
						result = (diffX < boundary && diffX > -boundary) && (diffY > delta);
						break;
					case 'bottom':
						result = (diffX < boundary && diffX > -boundary) && (diffY < -delta);
						break;
				}

				if (result) {
					touchPosX = null;
					touchPosY = null;
					hide();
					return false;
				}
			}

			// Prevent vertical scrolling past the top or bottom
			if ((element.scrollTop < 0 && diffY < 0) ||
				(ts > (th - 2) && ts < (th + 2) && diffY > 0)) {
				event.preventDefault();
				event.stopPropagation();
			}
		});

		// Prevent events from bubbling
		['click', 'touchend', 'touchstart', 'touchmove'].forEach(function(eventType) {
			element.addEventListener(eventType, function(event) {
				event.stopPropagation();
			});
		});

		// Hide if clicking anchor pointing to panel ID
		element.addEventListener('click', function(event) {
			var link = event.target.closest('a[href="#' + id + '"]');
			if (link) {
				event.preventDefault();
				event.stopPropagation();
				config.target.classList.remove(config.visibleClass);
			}
		});

		// Toggle on anchor click (check this first before body click hide)
		body.addEventListener('click', function(event) {
			var link = event.target.closest('a[href="#' + id + '"]');
			if (link) {
				event.preventDefault();
				event.stopPropagation();
				config.target.classList.toggle(config.visibleClass);
			}
		});

		// Body click/tap to hide (but not if clicking the toggle link)
		body.addEventListener('click', function(event) {
			var link = event.target.closest('a[href="#' + id + '"]');
			if (link) return; // Don't hide if clicking the toggle
			hide(event);
		});
		body.addEventListener('touchend', function(event) {
			var link = event.target.closest('a[href="#' + id + '"]');
			if (link) return; // Don't hide if clicking the toggle
			hide(event);
		});

		// Hide on ESC
		if (config.hideOnEscape) {
			window.addEventListener('keydown', function(event) {
				if (event.keyCode === 27) {
					hide(event);
				}
			});
		}

		return element;
	}

	/**
	 * Smooth scroll to an element
	 * @param {string} selector - CSS selector for target element
	 * @param {object} options - Configuration options
	 */
	function scrollTo(selector, options) {
		var defaults = {
			offset: 0
		};
		var config = Object.assign({}, defaults, options);
		var target = document.querySelector(selector);
		
		if (!target) return;

		var offsetValue = typeof config.offset === 'function' ? config.offset() : config.offset;
		var targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offsetValue;

		window.scrollTo({
			top: targetPosition,
			behavior: 'smooth'
		});
	}

	/**
	 * Initialize scrolly behavior on elements
	 * @param {string} selector - CSS selector for scrolly links
	 * @param {object} options - Configuration options
	 */
	function initScrolly(selector, options) {
		var links = document.querySelectorAll(selector);
		
		links.forEach(function(link) {
			link.addEventListener('click', function(event) {
				var href = link.getAttribute('href');
				if (!href || href.charAt(0) !== '#' || href.length < 2) return;

				event.preventDefault();
				scrollTo(href, options);
			});
		});
	}

	// Expose to global namespace
	window.MBUtil = {
		navList: navList,
		panel: panel,
		scrollTo: scrollTo,
		initScrolly: initScrolly
	};

})();
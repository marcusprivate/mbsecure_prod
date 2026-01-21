
/**
 * Main JavaScript for MB Secure website (vanilla JS)
 */
(function() {
	'use strict';

	var body = document.body;
	var nav = document.getElementById('nav');

	// Breakpoints
	breakpoints({
		xlarge:  [ '1281px',  '1680px' ],
		large:   [ '981px',   '1280px' ],
		medium:  [ '737px',   '980px'  ],
		small:   [ '361px',   '736px'  ],
		xsmall:  [ null,      '360px'  ]
	});

	// Scrolly - smooth scroll for anchor links
	MBUtil.initScrolly('.scrolly', {
		offset: function() { return nav ? nav.offsetHeight - 5 : 0; }
	});

	// Nav

	// Title Bar
	var getBasePathFn = (typeof MBSecure !== 'undefined') ? MBSecure.getBasePath : 
	                    (typeof getBasePath === 'function') ? getBasePath : function() { return ''; };
	var basePath = getBasePathFn();
	var logoSrc = basePath + 'images/logo.png';
	var homeHref = basePath || '/';

	var titleBar = document.createElement('div');
	titleBar.id = 'titleBar';
	titleBar.innerHTML = 
		'<span class="title"><a href="' + homeHref + '"><img src="' + logoSrc + '" alt="MB Secure" class="logo-img-small" /></a></span>' +
		'<a href="#navPanel" class="toggle">' +
			'<span class="hamburger">' +
				'<span class="hamburger-line"></span>' +
				'<span class="hamburger-line"></span>' +
				'<span class="hamburger-line"></span>' +
			'</span>' +
		'</a>';
	body.appendChild(titleBar);

	// Backdrop overlay
	var navBackdrop = document.createElement('div');
	navBackdrop.id = 'navBackdrop';
	body.appendChild(navBackdrop);

	// Panel
	var navPanel = document.createElement('div');
	navPanel.id = 'navPanel';
	navPanel.innerHTML = '<nav>' + MBUtil.navList(nav) + '</nav>';
	body.appendChild(navPanel);

	MBUtil.panel(navPanel, {
		delay: 0,
		hideOnClick: true,
		hideOnSwipe: true,
		resetScroll: true,
		resetForms: true,
		side: 'right',
		target: body,
		visibleClass: 'navPanel-visible'
	});

	// Auto-close on nav link click
	navPanel.addEventListener('click', function(e) {
		var link = e.target.closest('.link');
		if (!link) return;

		var href = link.getAttribute('href');
		if (href && href.indexOf('#') === 0) {
			e.preventDefault();
			navPanel._hide();
			// Scroll to section after panel closes
			setTimeout(function() {
				MBUtil.scrollTo(href, { offset: 55 });
			}, 300);
		}
	});

	// Backdrop click closes panel
	navBackdrop.addEventListener('click', function() {
		navPanel._hide();
	});

	// Fade out body on navigation to prevent flicker on rapid clicks
	document.addEventListener('click', function(e) {
		var link = e.target.closest('a');
		if (!link) return;

		var href = link.getAttribute('href');
		var target = link.getAttribute('target');
		
		// Only handle internal navigation links (not #anchors, not external, not blank targets, not lightbox)
		if (href && 
			href.indexOf('#') !== 0 && 
			href.indexOf('http') !== 0 && 
			href.indexOf('mailto:') !== 0 && 
			href.indexOf('tel:') !== 0 &&
			target !== '_blank' &&
			!link.classList.contains('glightbox')) {
			body.classList.add('navigating-away');
		}
	});

	// Remove preload class after page loads
	window.addEventListener('load', function() {
		setTimeout(function() {
			body.classList.remove('is-preload');
		}, 100);
	});

})();
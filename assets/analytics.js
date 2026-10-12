(function () {
  'use strict';
  if (window.LCBridgeAnalytics) return;
  var config = window.LCBridgeAnalyticsConfig || {};
  var consent = 'denied';
  var loaded = false;
  var pageViewed = false;
  var measurementId = /^G-[A-Z0-9]+$/.test(config.ga4MeasurementId || '') ? config.ga4MeasurementId : '';
  var product = location.pathname.indexOf('/community-agents/') === 0 ? 'community_agents' :
    location.pathname.indexOf('/docusign-integration/') === 0 ? 'docusign' :
    location.pathname.indexOf('/highlevel-development/') === 0 ? 'custom_development' : 'company';

  function send(name, properties) {
    var event = Object.assign({ event: name, product: product, page_path: location.pathname }, properties || {});
    // This queue stays in memory. URLs with query strings, form values and PII
    // never enter it. A consented configured adapter is required for transmission.
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(event);
    document.dispatchEvent(new CustomEvent('lcbridge:analytics', { detail: event }));
    if (loaded && consent === 'granted') {
      var payload = Object.assign({}, event);
      delete payload.event;
      payload.page_location = location.origin + location.pathname;
      payload.page_referrer = document.referrer ? new URL(document.referrer).origin : '';
      window.gtag('event', name, payload);
    }
  }

  function setConsent(value) {
    consent = value === 'granted' ? 'granted' : 'denied';
    if (!measurementId) return;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    if (loaded) {
      window.gtag('consent', 'update', { analytics_storage: consent, ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
      if (consent === 'granted' && !pageViewed) { pageViewed = true; send('page_view'); }
      return;
    }
    if (consent !== 'granted') return;
    window.gtag('consent', 'default', { analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
    window.gtag('js', new Date());
    window.gtag('config', measurementId, { send_page_view: false,
      page_location: location.origin + location.pathname,
      page_referrer: document.referrer ? new URL(document.referrer).origin : '' });
    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
    document.head.appendChild(script);
    loaded = true;
    pageViewed = true;
    send('page_view');
  }

  document.addEventListener('click', function (event) {
    var link = event.target.closest('a');
    if (!link) return;
    var target;
    try { target = new URL(link.href, location.href); } catch (_) { return; }
    var action = link.dataset.analyticsAction;
    if (!action && target.hostname === 'community-agents.lcbridge.app' && target.pathname === '/oauth/install') action = 'install_cta_clicked';
    if (!action && target.hash === '#apply' && target.pathname.indexOf('/docusign-integration/') === 0) action = 'trial_cta_clicked';
    if (!action && target.pathname.indexOf('book-a-call') !== -1) action = 'booking_cta_clicked';
    if (!action && /(?:youtube\.com|youtu\.be)$/.test(target.hostname)) action = 'demo_play_clicked';
    if (!action) return;
    var section = link.closest('section,nav,footer,header');
    send(action, { cta_location: section ? section.id || section.tagName.toLowerCase() : 'page',
      destination_host: target.hostname, destination_path: target.pathname });
  });

  window.LCBridgeAnalytics = { setConsent: setConsent,
    recordProjectInquiryEvent: function (name) {
      if (product !== 'custom_development') return;
      if (['project_form_started', 'project_form_error', 'project_form_accepted'].indexOf(name) === -1) return;
      send(name);
    },
    // Conversion confirmation must come from a trusted success page or backend.
    // A click or an iframe load is never a completed trial, installation or sale.
    confirmConversion: function (name, productName) {
      if (['trial_request_completed', 'installation_completed', 'subscription_completed'].indexOf(name) === -1) return;
      if (['docusign', 'community_agents'].indexOf(productName) === -1) return;
      send(name, { product: productName });
    } };
})();

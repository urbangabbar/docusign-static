(function () {
  'use strict';
  if (window.LCBridgeAnalytics) return;
  var config = window.LCBridgeAnalyticsConfig || {};
  var consent = 'denied';
  var loaded = false;
  var pageViewed = false;
  var CONSENT_REGIONS = ['AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU','IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE','IS','LI','NO','GB','CH'];
  var measurementId = /^G-[A-Z0-9]+$/.test(config.ga4MeasurementId || '') ? config.ga4MeasurementId : '';
  // GA4 reads campaign source from page_location, so keep plain utm_* values and drop every other parameter.
  var UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  function pageLocation() {
    var params = new URL(location.href).searchParams, kept = [];
    UTM_KEYS.forEach(function (key) {
      var value = params.get(key);
      if (value && /^[A-Za-z0-9_.|+ -]{1,100}$/.test(value)) kept.push(key + '=' + encodeURIComponent(value));
    });
    return location.origin + location.pathname + (kept.length ? '?' + kept.join('&') : '');
  }
  var sheetsPage = location.pathname.indexOf('/google-sheets-integration/') === 0 ||
    Boolean(document.documentElement && document.documentElement.hasAttribute('data-sheets-generated')) ||
    (location.pathname === '/book-a-call/' && new URL(location.href).searchParams.get('product') === 'google-sheets');
  var product = sheetsPage ? 'google_sheets' : location.pathname.indexOf('/community-agents/') === 0 ? 'community_agents' :
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
      payload.page_location = pageLocation();
      payload.page_referrer = document.referrer ? new URL(document.referrer).origin : '';
      window.gtag('event', name, payload);
    }
  }

  // explicit === false is the no-choice-yet default: analytics on, except where
  // Consent Mode's region default keeps EEA/UK/CH visitors cookieless until they opt in.
  function setConsent(value, explicit) {
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
    window.gtag('consent', 'default', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', region: CONSENT_REGIONS });
    window.gtag('consent', 'default', { analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
    if (explicit !== false) window.gtag('consent', 'update', { analytics_storage: 'granted' });
    window.gtag('js', new Date());
    window.gtag('config', measurementId, { send_page_view: false,
      page_location: pageLocation(),
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
    if (!action && target.pathname === '/google-sheets-integration/' && target.hash === '#apply') action = 'early_access_cta_clicked';
    if (!action && target.hash === '#apply' && target.pathname.indexOf('/docusign-integration/') === 0) action = 'trial_cta_clicked';
    if (!action && target.pathname.indexOf('book-a-call') !== -1) action = 'booking_cta_clicked';
    if (!action && /(?:youtube\.com|youtu\.be)$/.test(target.hostname)) action = 'demo_play_clicked';
    if (!action) return;
    var section = link.closest('section,nav,footer,header');
    send(action, { cta_location: section ? section.id || section.tagName.toLowerCase() : 'page',
      destination_host: target.hostname, destination_path: target.pathname,
      product: target.pathname.indexOf('/google-sheets-integration/') === 0 || target.searchParams.get('product') === 'google-sheets' ? 'google_sheets' : product });
  });

  window.LCBridgeAnalytics = { setConsent: setConsent,
    recordSheetsEvent: function (name, properties) {
      if (!sheetsPage) return;
      if (['template_preview_opened', 'template_filter_changed', 'pricing_calculator_used',
           'early_access_form_started', 'early_access_form_error', 'sales_interest'].indexOf(name) === -1) return;
      var safe = {};
      var ids = ["overview", "leads", "pipeline", "bookings", "sales", "daily", "team", "response", "cash", "stages", "forecast", "payments", "receivables", "invoice-items", "subscriptions", "subscription-changes", "orders", "products", "conversations", "messages", "capture", "customer-payments", "businesses", "activities", "custom-records"];
      if (properties && ids.indexOf(properties.template_id) !== -1) safe.template_id = properties.template_id;
      send(name, safe);
    },
    recordProjectInquiryEvent: function (name) {
      if (product !== 'custom_development') return;
      if (['project_form_started', 'project_form_error', 'project_form_accepted'].indexOf(name) === -1) return;
      send(name);
    },
    // Conversion confirmation must come from a trusted success page or backend.
    // A click or an iframe load is never a completed trial, installation or sale.
    confirmConversion: function (name, productName) {
      if (name === 'early_access_request_accepted' && productName === 'google_sheets') { send(name, { product: productName }); return; }
      if (['trial_request_completed', 'installation_completed', 'subscription_completed'].indexOf(name) === -1) return;
      if (['docusign', 'community_agents'].indexOf(productName) === -1) return;
      send(name, { product: productName });
    } };
})();

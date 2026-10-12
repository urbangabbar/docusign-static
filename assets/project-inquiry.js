(function () {
  'use strict';
  var form = document.getElementById('lcbridge-custom-development');
  if (!form || !window.fetch) return;
  var button = form.querySelector('button[type="submit"]');
  var status = document.getElementById('project-form-status');
  var trackingId = 'tk_164784dde1924bafbe68a7a157d77220';
  var trackerPromise;
  var pending = false;
  var captured = false;
  var attempts = 0;
  var timer;
  var nativeFetch = window.fetch;
  var started = false;

  function record(name) {
    if (window.LCBridgeAnalytics && window.LCBridgeAnalytics.recordProjectInquiryEvent) {
      window.LCBridgeAnalytics.recordProjectInquiryEvent(name);
    }
  }
  form.addEventListener('input', function () {
    if (!started) { started = true; record('project_form_started'); }
  });
  form.addEventListener('invalid', function () { record('project_form_error'); }, true);

  function message(text, state) {
    status.textContent = text;
    status.dataset.state = state || '';
  }
  function lockFields(value) {
    form.querySelectorAll('input, textarea').forEach(function (field) { field.readOnly = value; });
  }
  function fail(text) {
    if (!pending) return;
    clearTimeout(timer);
    pending = false;
    lockFields(false);
    button.disabled = false;
    button.textContent = 'Send project brief →';
    form.removeAttribute('aria-busy');
    message(text, 'error');
    record('project_form_error');
  }
  function succeed() {
    if (!pending) return;
    clearTimeout(timer);
    pending = false;
    captured = true;
    form.removeAttribute('aria-busy');
    form.querySelectorAll('.dev-field, .dev-form-note, button').forEach(function (node) { node.hidden = true; });
    message('Thanks—our team will review your brief and follow up with questions and a suggested next step.', 'success');
    status.tabIndex = -1;
    status.focus();
    // This event is HTTP acceptance, not a confirmed CRM conversion. No form
    // values enter analytics; CRM records and stages remain the source of truth.
    record('project_form_accepted');
  }

  // The vendor currently has no acknowledgement event and catches its own
  // errors. Observe only this form's vendor-generated fetch; leave every
  // request, response and the vendor's retry mechanism unchanged.
  window.fetch = function (input, options) {
    var relevant = false;
    try {
      var url = new URL(typeof input === 'string' ? input : input.url, location.href);
      var payload = options && typeof options.body === 'string' ? JSON.parse(options.body) : null;
      relevant = pending && url.origin === 'https://backend.leadconnectorhq.com' &&
        url.pathname === '/external-tracking/events' && payload &&
        payload.type === 'external_form_submission' && payload.trackingId === trackingId && payload.formId === form.id;
    } catch (_) { /* Other requests do not concern this form. */ }
    if (relevant) attempts++;
    var request = nativeFetch.apply(this, arguments);
    if (relevant) request.then(function (response) {
      if (response.ok) succeed();
      else if (attempts >= 4) fail('We couldn’t send your inquiry. Your brief is still here—please try again or email us.');
    }, function () {
      if (attempts >= 4) fail('We couldn’t connect. Your brief is still here—please try again or email us.');
    });
    return request;
  };

  function loadTracker() {
    if (trackerPromise) return trackerPromise;
    trackerPromise = new Promise(function (resolve, reject) {
      var script = document.createElement('script');
      // Copied from LC Bridge → Settings → External Tracking. Load only when
      // someone submits an inquiry, rather than track every page visitor.
      script.src = 'https://link.msgsndr.com/js/external-tracking.js';
      script.setAttribute('data-tracking-id', trackingId);
      script.onload = resolve;
      script.onerror = function () { script.remove(); trackerPromise = null; reject(new Error('Tracker unavailable')); };
      document.body.appendChild(script);
    });
    return trackerPromise;
  }

  // HighLevel also captures submit-button clicks, even when HTML validation
  // fails. Route clicks through requestSubmit so only valid forms reach it.
  document.addEventListener('click', function (event) {
    if (!button.contains(event.target)) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    if (!pending && !captured) form.requestSubmit();
  }, true);

  // This capture listener runs before the lazily loaded tracker. It blocks
  // duplicate/invalid submit events, and then lets one valid event reach it.
  var release = false;
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    if (release) { release = false; return; }
    event.stopImmediatePropagation();
    if (pending || captured || !form.reportValidity()) return;
    if (!form.elements.full_name.value.trim() || !form.elements.project_description.value.trim()) {
      message('Please add your name and a few words about your project.', 'error');
      record('project_form_error');
      (!form.elements.full_name.value.trim() ? form.elements.full_name : form.elements.project_description).focus();
      return;
    }
    pending = true;
    lockFields(true);
    attempts = 0;
    button.disabled = true;
    button.textContent = 'Sending…';
    form.setAttribute('aria-busy', 'true');
    message('Sending your project brief…');
    timer = setTimeout(function () {
      // A slow vendor request might still complete. Keep the form locked to
      // avoid duplicate inquiries, and never assert that it was received.
      message('We haven’t received confirmation yet. Please keep this page open, or email us if you need help.', 'error');
    }, 30000);
    loadTracker().then(function () {
      release = true;
      form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    }).catch(function () { fail('The form couldn’t connect. Your brief is still here—please try again or email us.'); });
  }, true);
  button.disabled = false;
})();

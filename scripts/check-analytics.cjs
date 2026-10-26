/* Verify meaningful tracking boundaries without transmitting analytics. */
const vm = require('node:vm');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const source = fs.readFileSync(require('node:path').join(__dirname, '../assets/analytics.js'), 'utf8');

function run(id, pathname = '/community-agents/') {
  const listeners = {};
  const requests = [];
  const document = {
    referrer: 'https://example.com/private?email=person@example.com',
    addEventListener(name, callback) { listeners[name] = callback; },
    dispatchEvent() {},
    createElement() { return {}; },
    head: { appendChild(script) { requests.push(script.src); } }
  };
  const context = { window: { LCBridgeAnalyticsConfig: { ga4MeasurementId: id } }, document,
    location: { pathname, origin: 'https://lcbridge.app',
      href: 'https://lcbridge.app' + pathname + '?email=person@example.com' },
    URL, CustomEvent: function (name, options) { this.detail = options.detail; } };
  vm.runInNewContext(source, context);
  const link = { href: 'https://community-agents.lcbridge.app/oauth/install?email=person@example.com',
    dataset: {}, closest() { return { id: 'hero', tagName: 'SECTION' }; } };
  listeners.click({ target: { closest() { return link; } } });
  const events = context.window.dataLayer;
  assert.equal(events[0].event, 'install_cta_clicked');
  assert.equal(events[0].destination_path, '/oauth/install');
  assert.equal(events.some(event => /completed/.test(event.event || '')), false);
  assert.equal(JSON.stringify(events).includes('person@example.com'), false);
  assert.equal(requests.length, 0);
  const beforeInquiry = events.length;
  context.window.LCBridgeAnalytics.recordProjectInquiryEvent('person@example.com');
  assert.equal(events.length, beforeInquiry, 'Arbitrary values cannot enter inquiry analytics');
  for (const eventName of ['project_form_started', 'project_form_error', 'project_form_accepted']) {
    context.window.LCBridgeAnalytics.recordProjectInquiryEvent(eventName);
  }
  assert.equal(events.length, beforeInquiry + (pathname === '/highlevel-development/' ? 3 : 0));
  if (pathname === '/highlevel-development/') {
    assert.equal(events.at(-1).product, 'custom_development');
    assert.equal(events.at(-1).event, 'project_form_accepted');
    assert.equal(events.some(event => /completed|conversion/.test(event.event || '')), false);
  }
  assert.equal(requests.length, 0, 'Inquiry events do not bypass analytics consent');
  context.window.LCBridgeAnalytics.setConsent('denied');
  assert.equal(requests.length, 0);
  context.window.LCBridgeAnalytics.setConsent('granted');
  assert.equal(requests.length, id ? 1 : 0);
  context.window.LCBridgeAnalytics.confirmConversion('form_loaded', 'community_agents');
  assert.equal(events.some(event => event.event === 'form_loaded'), false);
  context.window.LCBridgeAnalytics.confirmConversion('installation_completed', 'community_agents');
  assert.equal(events.some(event => event.event === 'installation_completed'), true);
  assert.equal(JSON.stringify(events).includes('person@example.com'), false);
}
{ // No choice yet: GA4 loads by default, with EEA/UK/CH denied through Consent Mode's region default.
  const requests = [];
  const ctx = { window: { LCBridgeAnalyticsConfig: { ga4MeasurementId: 'G-TEST123' } },
    document: { referrer: '', addEventListener() {}, dispatchEvent() {}, createElement() { return {}; }, head: { appendChild(s) { requests.push(s.src); } } },
    location: { pathname: '/', origin: 'https://lcbridge.app', href: 'https://lcbridge.app/' }, URL, CustomEvent: function () {} };
  vm.runInNewContext(source, ctx);
  ctx.window.LCBridgeAnalytics.setConsent('granted', false);
  const consents = ctx.window.dataLayer.filter(a => a[0] === 'consent').map(a => Array.from(a));
  assert.equal(requests.length, 1);
  assert.ok(consents.some(c => c[1] === 'default' && c[2].analytics_storage === 'denied' && c[2].region.includes('GB') && c[2].region.includes('DE')));
  assert.ok(!consents.some(c => c[1] === 'update'), 'A default load never overrides the regional denial');
  assert.ok(consents.every(c => c[2].ad_storage === undefined || c[2].ad_storage === 'denied'));
}
run('');
run('G-TEST123');
run('G-TEST123', '/highlevel-development/');
console.log('Analytics boundaries passed: no pre-consent requests, no PII/query strings, clicks are not conversions.');

for (const pathname of ['/google-sheets-integration/templates/pipeline-follow-up/', '/blog/connect-gohighlevel-google-sheets/']) {
  const events = [], requests = [];
  const context = { window: { dataLayer: events }, document: {
    referrer: '', documentElement: { hasAttribute: name => name === 'data-sheets-generated' },
    addEventListener() {}, dispatchEvent() {}, createElement() { return {}; },
    head: { appendChild(script) { requests.push(script.src); } }
  }, location: { pathname, origin: 'https://lcbridge.app', href: 'https://lcbridge.app' + pathname },
  URL, CustomEvent: function () {} };
  vm.runInNewContext(source, context);
  const api = context.window.LCBridgeAnalytics;
  api.recordSheetsEvent('template_preview_opened', { template_id: 'pipeline', email: 'person@example.com' });
  api.recordSheetsEvent('template_filter_changed', { template_id: 'person@example.com' });
  api.recordSheetsEvent('early_access_form_started');
  api.recordSheetsEvent('pricing_calculator_used');
  api.recordSheetsEvent('arbitrary_person@example.com');
  assert.equal(events.length, 4);
  assert.equal(events[0].template_id, 'pipeline');
  assert.equal(events[1].template_id, undefined);
  assert.equal(events.every(event => event.product === 'google_sheets'), true);
  assert.equal(events.some(event => /accepted|completed/.test(event.event)), false);
  api.confirmConversion('iframe_loaded', 'google_sheets');
  assert.equal(events.length, 4);
  api.confirmConversion('early_access_request_accepted', 'google_sheets');
  assert.equal(events.at(-1).event, 'early_access_request_accepted');
  assert.equal(JSON.stringify(events).includes('person@example.com'), false);
  assert.equal(requests.length, 0);
}
console.log('Google Sheets analytics passed: allowlisted events, no private fields, and explicit acceptance only.');

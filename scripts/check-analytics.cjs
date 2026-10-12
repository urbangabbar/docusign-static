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
run('');
run('G-TEST123');
run('G-TEST123', '/highlevel-development/');
console.log('Analytics boundaries passed: no pre-consent requests, no PII/query strings, clicks are not conversions.');

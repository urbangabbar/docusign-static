/* Verify meaningful tracking boundaries without transmitting analytics. */
const vm = require('node:vm');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const source = fs.readFileSync(require('node:path').join(__dirname, '../assets/analytics.js'), 'utf8');

function run(id) {
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
    location: { pathname: '/community-agents/', origin: 'https://lcbridge.app',
      href: 'https://lcbridge.app/community-agents/?email=person@example.com' },
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
console.log('Analytics boundaries passed: no pre-consent requests, no PII/query strings, clicks are not conversions.');

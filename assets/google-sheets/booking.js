(function () {
  'use strict';
  if (new URL(location.href).searchParams.get('product') !== 'google-sheets') return;
  var root = document.querySelector('.bk');
  root.querySelector('h1').textContent = 'Let’s make Google Sheets pricing work for you.';
  root.querySelector('.sub').textContent = 'Talk with LC Bridge about your GoHighLevel data volumes, refresh frequency, and a custom subscription with more predictable costs. We want you to be happy with both the product and the price.';
  var points = [
    ['Your workload.', 'Which records you transfer, how many accounts you connect, and how frequently your imports run.'],
    ['Predictable costs.', 'Discuss a custom subscription for high-volume usage. Scope, rates, and any limits are agreed together.'],
    ['Your reporting needs.', 'The templates, source history, and reviewed updates your team needs during early access.'],
    ['A fair fit.', 'Tell us if usage pricing gets in the way. We’ll work with you on a deal that makes sense for your team.']
  ];
  root.querySelectorAll('.cov li span').forEach(function (span, index) {
    span.textContent = '';
    var strong = document.createElement('b');
    strong.textContent = points[index][0] + ' ';
    span.append(strong, points[index][1]);
  });
  root.querySelector('.cal-h').textContent = 'Talk to our team';
  root.querySelector('.cal-p').textContent = 'Choose a time with LC Bridge. Mention Google Sheets and your expected record transfers in the booking notes.';
  var frame = root.querySelector('iframe');
  frame.title = 'Talk to LC Bridge Sales about Google Sheets integration';
  var trial = document.querySelector('.nav .lcb-btn--trial');
  if (trial) { trial.href = '/google-sheets-integration/#apply'; trial.textContent = 'Get early access'; }
  var pricing = document.querySelector('#explore a[href="/docusign-integration/pricing"]');
  if (pricing) {
    pricing.href = '/google-sheets-integration/pricing/';
    pricing.querySelector('.xl-t').textContent = 'Google Sheets pricing →';
    pricing.querySelector('.xl-d').textContent = 'Planned usage rates, volume discounts, and an optional transfer calculator.';
  }
  window.LCBridgeAnalytics?.recordSheetsEvent('sales_interest');
})();

// RB2B visitor identification on every page that loads this file. Loads by default
// (disclosed in the analytics dialog); skipped once the visitor chose "Keep analytics off".
(function () {
  var off = false;
  try { off = localStorage.getItem('lcbridge-analytics-consent') === 'denied'; } catch (_) {}
  if (off || window.reb2b) return;
  window.reb2b = { loaded: true };
  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://ddwl4m2hdecbv.cloudfront.net/b/4N210HXWG76Z/4N210HXWG76Z.js.gz';
  document.head.appendChild(s);
})();

(function () {
  'use strict';
  var menus = document.querySelectorAll('[data-product-switcher]');
  menus.forEach(function (menu) {
    menu.addEventListener('click', function (event) { if (event.target.closest('a')) menu.open = false; });
    document.addEventListener('click', function (event) { if (!menu.contains(event.target)) menu.open = false; });
    menu.addEventListener('keydown', function (event) { if (event.key === 'Escape') { menu.open = false; menu.querySelector('summary').focus(); } });
    menu.addEventListener('toggle', function () { if (menu.open) menus.forEach(function (other) { if (other !== menu) other.open = false; }); });
  });
  var dialog = document.querySelector('#analytics-dialog');
  if (!dialog) return;
  var preference;
  try { preference = localStorage.getItem('lcbridge-analytics-consent'); } catch (_) {}
  if (preference === 'granted' || preference === 'denied') window.LCBridgeAnalytics?.setConsent(preference);
  if (!window.LCBridgeAnalyticsConfig?.ga4MeasurementId) document.querySelector('#analytics-description').textContent = 'Optional analytics are not currently enabled, except RB2B visitor identification on every page and the Meta pixel on the Google Sheets campaign page, which Keep analytics off stops. You can save your preference for when a measurement stream is configured. Hosted forms have their own provider controls.';
  document.querySelector('#analytics-settings').addEventListener('click', function () { dialog.showModal(); });
  dialog.querySelectorAll('[data-analytics-consent]').forEach(function (button) {
    button.addEventListener('click', function () {
      var choice = button.dataset.analyticsConsent;
      window.LCBridgeAnalytics?.setConsent(choice);
      try { localStorage.setItem('lcbridge-analytics-consent', choice); } catch (_) {}
      dialog.close();
    });
  });
})();

// A company menu encloses the product picker on small screens.
document.querySelectorAll('[data-company-menu], .lcb-product-header details').forEach(function (menu) {
  menu.addEventListener('click', function (event) { if (event.target.closest('a')) menu.open = false; });
  document.addEventListener('click', function (event) { if (!menu.contains(event.target)) menu.open = false; });
  menu.addEventListener('keydown', function (event) { if (event.key === 'Escape') { menu.open = false; menu.querySelector('summary').focus(); } });
});

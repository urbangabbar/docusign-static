/* A linked thumbnail works without JS. Screens marked data-autoplay start muted when
   half visible; a big "Tap to unmute" button then restarts the film from 0:00 with sound.
   Visitors who opted out (Keep analytics off, GPC), or use reduced motion or Save-Data, keep click-to-play. */
(function () {
  'use strict';
  var optedOut = navigator.globalPrivacyControl === true;
  try { optedOut = optedOut || localStorage.getItem('lcbridge-analytics-consent') === 'denied'; } catch (_) {}
  var quiet = optedOut || window.matchMedia('(prefers-reduced-motion: reduce)').matches ||
    Boolean(navigator.connection && navigator.connection.saveData);
  var speaker = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M3 9v6h4l5 4V5L7 9H3zm13.5 3a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4zM14 3.2v2.1a7 7 0 0 1 0 13.4v2.1a9 9 0 0 0 0-17.6z"/></svg>';

  function frameFor(screen, id, muted) {
    var frame = document.createElement('iframe');
    frame.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&playsinline=1&rel=0&' +
      (muted ? 'mute=1&controls=0&cc_load_policy=0&loop=1&playlist=' + id : 'cc_load_policy=0');
    frame.title = screen.dataset.videoTitle || 'LC Bridge product video';
    frame.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    frame.allowFullscreen = true;
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    return frame;
  }

  document.querySelectorAll('[data-youtube-video]').forEach(function (screen) {
    var play = screen.querySelector('.lcb-video-trigger');
    var id = screen.dataset.youtubeVideo || '';
    if (!play || !/^[A-Za-z0-9_-]{11}$/.test(id)) return;
    var container = screen.closest('[data-state]');

    play.addEventListener('click', function (event) {
      event.preventDefault();
      var frame = frameFor(screen, id, false);
      if (container) container.dataset.state = 'on';
      screen.classList.remove('lcb-video-muted');
      screen.replaceChildren(frame);
      frame.focus();
    }, { once: true });

    if (!('autoplay' in screen.dataset) || quiet || !('IntersectionObserver' in window)) return;
    new IntersectionObserver(function (entries, observer) {
      if (!entries[0].isIntersecting) return;
      observer.disconnect();
      var preview = frameFor(screen, id, true);
      preview.tabIndex = -1;
      preview.setAttribute('aria-hidden', 'true');
      preview.className = 'lcb-video-preview';
      screen.insertBefore(preview, play);
      screen.classList.add('lcb-video-muted');
      if (container) container.dataset.state = 'muted';
      var label = play.querySelector('.lcb-video-label, .home-video-play');
      if (label) label.innerHTML = speaker + 'Tap to unmute';
      play.setAttribute('aria-label', 'Unmute and watch from the start');
    }, { threshold: 0.5 }).observe(screen);
  });

  var style = document.createElement('style');
  style.textContent =
    '.lcb-video-muted{position:relative}' +
    '.lcb-video-muted .lcb-video-preview{position:absolute;inset:0;width:100%;height:100%;border:0;z-index:2;pointer-events:none}' +
    '.lcb-video-muted .lcb-video-poster{visibility:hidden}.lcb-video-muted .lcb-video-trigger>img{display:none!important}' +
    '.lcb-video-muted .lcb-video-trigger{position:absolute;inset:0;z-index:3;display:flex!important;align-items:center!important;justify-content:center!important;padding:0!important;background:transparent!important}' +
    '.lcb-video-muted :is(.lcb-video-label,.home-video-play){position:static!important;transform:none!important;display:inline-flex;align-items:center;gap:10px;min-height:56px;padding:14px 26px!important;border:0!important;border-radius:999px!important;background:#0b1220e6!important;color:#fff!important;font:700 18px/1.2 Inter,system-ui,sans-serif!important;box-shadow:0 10px 30px #0006}' +
    '.lcb-video-muted :is(.lcb-video-label,.home-video-play) svg{width:24px;height:24px;flex:none}' +
    '.lcb-video-muted .lcb-video-trigger:hover :is(.lcb-video-label,.home-video-play){background:#0b1220!important}' +
    '@media(max-width:500px){.lcb-video-muted :is(.lcb-video-label,.home-video-play){min-height:48px;padding:12px 20px!important;font-size:16px!important}}';
  document.head.appendChild(style);
})();

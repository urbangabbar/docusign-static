/* A linked thumbnail works without JS; a deliberate click mounts one player. */
(function () {
  'use strict';
  document.querySelectorAll('[data-youtube-video]').forEach(function (screen) {
    var play = screen.querySelector('.lcb-video-trigger');
    if (!play || !/^[A-Za-z0-9_-]{11}$/.test(screen.dataset.youtubeVideo || '')) return;
    play.addEventListener('click', function (event) {
      event.preventDefault();
      var frame = document.createElement('iframe');
      frame.src = 'https://www.youtube-nocookie.com/embed/' + screen.dataset.youtubeVideo +
        '?autoplay=1&playsinline=1&rel=0&cc_load_policy=1';
      frame.title = screen.dataset.videoTitle || 'LC Bridge product video';
      frame.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      frame.allowFullscreen = true;
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      var container = screen.closest('[data-state]');
      if (container) container.dataset.state = 'on';
      screen.replaceChildren(frame);
      frame.focus();
    }, { once: true });
  });
})();

/* Progressive enhancement: every product claim and price remains in the HTML. */
(() => {
  'use strict';
  const one = (selector) => document.querySelector(selector);
  const all = (selector) => [...document.querySelectorAll(selector)];
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  function track(event, properties = {}) {
    const payload = { event, product: 'docusign', ...properties };
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(payload);
    window.dispatchEvent(new CustomEvent('lcbridge:analytics', { detail: payload }));
  }
  const menu = one('.menu');
  const navigation = one('#navigation');
  function closeMenu() {
    menu.setAttribute('aria-expanded', 'false');
    menu.setAttribute('aria-label', 'Open navigation');
    navigation.classList.remove('is-open');
  }
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    navigation.classList.toggle('is-open', open);
  });
  navigation.addEventListener('click', (event) => {
    if (event.target.closest('a')) closeMenu();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') {
      closeMenu(); menu.focus();
    }
  });
  let video = one('#product-video-template').content.querySelector('iframe');
  const soundButton = one('.demo-sound');
  const demo = one('#demo');
  const videoId = video.dataset.videoId;
  let currentTime = 0;
  let lastTime = null;
  let playerState = -1;
  let demoStarted = false;
  const milestones = new Set();
  const watchedRanges = [];
  function watchedSeconds() {
    const merged = [];
    watchedRanges.sort((a, b) => a[0] - b[0]).forEach((range) => {
      const last = merged[merged.length - 1];
      if (last && range[0] <= last[1]) last[1] = Math.max(last[1], range[1]);
      else merged.push([...range]);
    });
    return merged.reduce((total, range) => total + range[1] - range[0], 0);
  }
  function mountDemo(muted, start = 0) {
    const next = video.cloneNode(false);
    const url = new URL('https://www.youtube-nocookie.com/embed/' + videoId);
    url.search = new URLSearchParams({ autoplay: '1', playsinline: '1', rel: '0',
      cc_load_policy: '1', enablejsapi: '1', mute: muted ? '1' : '0',
      controls: muted ? '0' : '1', origin: location.origin }).toString();
    if (start > 0) url.searchParams.set('start', String(Math.floor(start)));
    next.src = url.href;
    next.hidden = false;
    next.addEventListener('load', () => {
      next.contentWindow.postMessage(JSON.stringify({ event: 'listening', id: 1, channel: 'widget' }), url.origin);
    });
    if (video.isConnected) video.replaceWith(next);
    else one('.demo-shell').appendChild(next);
    video = next;
    lastTime = null;
    playerState = -1;
    one('.demo-cover').hidden = true;
    soundButton.hidden = !muted;
    demo.dataset.state = muted ? 'muted' : 'on';
    if (!muted) video.focus({ preventScroll: true });
  }
  function playDemo(event) {
    event.preventDefault();
    mountDemo(false, currentTime);
  }
  all('[data-play-demo]').forEach((button) => button.addEventListener('click', playDemo));
  soundButton.addEventListener('click', playDemo);
  window.addEventListener('message', (event) => {
    if (event.source !== video.contentWindow || event.origin !== 'https://www.youtube-nocookie.com' || typeof event.data !== 'string') return;
    let data;
    try { data = JSON.parse(event.data); } catch (_) { return; }
    const info = data.info && typeof data.info === 'object' ? data.info : {};
    if (Number.isFinite(info.playerState)) playerState = info.playerState;
    if (data.event === 'onStateChange' && Number.isFinite(data.info)) playerState = data.info;
    if (playerState === 1 && !demoStarted) { track('demo_started'); demoStarted = true; }
    if (Number.isFinite(info.currentTime)) {
      currentTime = info.currentTime;
      const delta = currentTime - lastTime;
      if (playerState === 1 && lastTime !== null && delta > 0 && delta <= 2) watchedRanges.push([lastTime, currentTime]);
      lastTime = currentTime;
    }
    if (Number.isFinite(info.duration) && info.duration > 0) {
      const progress = watchedSeconds() / info.duration * 100;
      [25, 50, 75].forEach((percent) => {
        if (progress >= percent && !milestones.has(percent)) {
          milestones.add(percent); track('demo_progress', { percent });
        }
      });
      if (playerState === 0 && progress >= 90 && !milestones.has(100)) {
        milestones.add(100); track('demo_completed');
      }
    }
  });
  // Keep the supplied thumbnail until a deliberate user play action.
  one('a[href="#transcript"]').addEventListener('click', () => {
    one('#transcript details').open = true;
  });
  const proofs = all('.data-proof, #workflow-proof, #record-proof');
  function animateProof(element) {
    if (reduced.matches) return;
    element.classList.remove('is-playing');
    void element.offsetWidth;
    element.classList.add('is-playing');
  }
  all('[data-replay]').forEach((button) => button.addEventListener('click', () => {
    const element = document.getElementById(button.dataset.replay);
    if (element) { animateProof(element); track('proof_replayed', { proof: element.id }); }
  }));
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) { animateProof(entry.target); observer.unobserve(entry.target); }
      });
    }, { threshold: 0.2 });
    proofs.forEach((element) => observer.observe(element));
  }
  all('[data-billing]').forEach((button) => button.addEventListener('click', () => {
    if (button.getAttribute('aria-pressed') === 'true') return;
    const period = button.dataset.billing;
    all('[data-billing]').forEach((option) => option.setAttribute('aria-pressed', String(option === button)));
    all('.amount').forEach((amount) => { amount.textContent = '$' + amount.dataset[period]; });
    all('.billing-note').forEach((note) => { note.textContent = note.dataset[period]; });
    track('billing_period_changed', { billing_period: period });
  }));
  let formRequested = false;
  function loadTrialForm() {
    if (formRequested) return;
    formRequested = true;
    const widget = one('#trial-widget');
    widget.appendChild(one('#trial-template').content.cloneNode(true));
    const iframe = widget.querySelector('iframe');
    iframe.addEventListener('load', () => {
      one('#trial-placeholder').hidden = true;
      track('trial_form_loaded'); // A form load is not a successful request or trial.
    }, { once: true });
    const script = document.createElement('script');
    script.src = 'https://link.msgsndr.com/js/form_embed.js';
    script.async = true;
    document.body.appendChild(script);
  }
  all('[data-trial-cta]').forEach((link) => link.addEventListener('click', () => {
    closeMenu();
    // The shared analytics click listener reports this intent once.
    loadTrialForm();
  }));
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) { loadTrialForm(); observer.disconnect(); }
    }, { rootMargin: '600px 0px' });
    observer.observe(one('#trial-widget'));
  } else {
    loadTrialForm();
  }
  if (location.hash === '#apply') loadTrialForm();
})();

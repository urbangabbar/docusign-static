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
  const video = one('#product-video');
  let demoStarted = false;
  const milestones = new Set();
  function playDemo(event) {
    event.preventDefault();
    if (!video.getAttribute('src')) {
      video.poster = video.dataset.poster;
      video.src = video.dataset.src;
      const captions = video.querySelector('track');
      captions.src = captions.dataset.src;
      one('.demo-cover').hidden = true;
      video.hidden = false;
      video.load();
    }
    video.focus({ preventScroll: true });
    video.play().catch(() => { /* Native controls remain available. */ });
  }
  all('[data-play-demo]').forEach((button) => button.addEventListener('click', playDemo));
  video.addEventListener('play', () => {
    if (!demoStarted) { track('demo_started'); demoStarted = true; }
  });
  video.addEventListener('timeupdate', () => {
    if (!video.duration || !Number.isFinite(video.duration)) return;
    let watched = 0;
    for (let i = 0; i < video.played.length; i++) watched += video.played.end(i) - video.played.start(i);
    const progress = watched / video.duration * 100;
    [25, 50, 75].forEach((percent) => {
      if (progress >= percent && !milestones.has(percent)) {
        milestones.add(percent); track('demo_progress', { percent });
      }
    });
  });
  video.addEventListener('ended', () => {
    let watched = 0;
    for (let i = 0; i < video.played.length; i++) watched += video.played.end(i) - video.played.start(i);
    if (watched >= video.duration * 0.9 && !milestones.has(100)) { milestones.add(100); track('demo_completed'); }
  });
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
    track('trial_cta_clicked', { location: link.dataset.trialCta, ...(link.dataset.plan ? { plan: link.dataset.plan } : {}) });
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

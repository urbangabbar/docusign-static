/* LC Bridge — site-wide "Book a call" pop-up.
   Any element with [data-book] opens a modal containing the HighLevel lead form.
   The iframe is lazy-loaded on first open; form_embed.js is injected once. */
(function () {
  var FORM_URL = "https://api.leadconnectorhq.com/widget/form/TO5PG5GbMdM5I72xnUX0";

  function init() {
    var modal = document.getElementById("bookModal");
    if (!modal) {
      modal = document.createElement("div");
      modal.className = "modal-overlay";
      modal.id = "bookModal";
      modal.setAttribute("aria-hidden", "true");
      modal.innerHTML =
        '<div class="modal-box" role="dialog" aria-modal="true" aria-label="Book a call with LC Bridge">' +
        '<button type="button" class="modal-close" data-book-close aria-label="Close">&times;</button>' +
        '<iframe class="modal-frame" data-src="' + FORM_URL + '" title="Book a call — LC Bridge" loading="lazy"></iframe>' +
        "</div>";
      document.body.appendChild(modal);
    }

    if (!document.querySelector('script[src*="form_embed.js"]')) {
      var s = document.createElement("script");
      s.src = "https://link.msgsndr.com/js/form_embed.js";
      s.async = true;
      document.body.appendChild(s);
    }

    var frame = modal.querySelector(".modal-frame");
    var baseSrc = frame.getAttribute("data-src") || "";
    var lastFocus = null;

    function open(e, trigger) {
      if (e) e.preventDefault();
      var intent = trigger && trigger.getAttribute("data-intent");
      var src = baseSrc + (intent ? (baseSrc.indexOf("?") > -1 ? "&" : "?") + "intent=" + encodeURIComponent(intent) : "");
      if (baseSrc && frame.getAttribute("src") !== src) { frame.src = src; }
      lastFocus = document.activeElement;
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
      document.body.classList.add("modal-lock");
      var c = modal.querySelector(".modal-close");
      if (c) c.focus();
    }

    function close() {
      modal.classList.remove("open");
      modal.setAttribute("aria-hidden", "true");
      document.body.classList.remove("modal-lock");
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }

    document.addEventListener("click", function (e) {
      var trigger = e.target.closest("[data-book]");
      if (trigger) { open(e, trigger); return; }
      if (e.target.closest("[data-book-close]")) { close(); return; }
      if (e.target === modal) { close(); }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && modal.classList.contains("open")) close();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

// Hero background video: smaller file on phones, and retry playback if the phone blocked autoplay.
(function () {
  var v = document.querySelector('.hero-media');
  if (!v) return;
  v.muted = true; v.defaultMuted = true; v.setAttribute('muted', '');
  v.src = window.matchMedia('(max-width: 900px)').matches ? v.dataset.srcMobile : v.dataset.src;
  function tryPlay() { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
  v.addEventListener('loadeddata', tryPlay);
  tryPlay();
  ['touchstart', 'scroll', 'click'].forEach(function (ev) {
    window.addEventListener(ev, function once() { if (v.paused) tryPlay(); window.removeEventListener(ev, once); }, { passive: true });
  });
  document.addEventListener('visibilitychange', function () { if (!document.hidden && v.paused) tryPlay(); });
})();

// Contact form: sends to FormSubmit (same service the old site used), then shows a confirmation.
(function () {
  var ENDPOINT = 'https://formsubmit.co/ajax/contact@plglegal.com';
  document.querySelectorAll('.case-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var status = form.querySelector('.form-status');
      var name = form.elements.name.value.trim();
      var phone = form.elements.phone.value.replace(/\D/g, '');
      var consent = form.elements.consent.checked;
      form.querySelectorAll('[aria-invalid]').forEach(function (el) { el.removeAttribute('aria-invalid'); });
      var bad = [];
      if (!name) bad.push(form.elements.name);
      if (phone.length < 10) bad.push(form.elements.phone);
      if (!consent) bad.push(form.elements.consent);
      if (bad.length) { bad.forEach(function (el) { el.setAttribute('aria-invalid', 'true'); }); bad[0].focus(); return; }
      if (form.elements._honey.value) return;
      var btn = form.querySelector('button[type=submit]');
      btn.disabled = true; status.textContent = form.dataset.sending;
      fetch(ENDPOINT, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (String(d.success) !== 'true') throw new Error(d.message || 'failed');
          form.reset(); status.textContent = form.dataset.ok; status.className = 'form-status ok';
          if (window.gtag) gtag('event', 'generate_lead', { method: 'website_form' });
        })
        .catch(function () { status.textContent = form.dataset.err; status.className = 'form-status err'; })
        .finally(function () { btn.disabled = false; });
    });
  });
  // Track phone and text clicks as conversions when Google tags are installed.
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="tel:"], a[href^="sms:"]');
    if (a && window.gtag) gtag('event', a.href.indexOf('tel:') === 0 ? 'phone_click' : 'text_click');
  });
  // Close the mobile menu when a link is chosen.
  document.querySelectorAll('.nav-mobile a').forEach(function (a) {
    a.addEventListener('click', function () { var d = a.closest('details'); if (d) d.removeAttribute('open'); });
  });
})();

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
  // Remember how the visitor arrived (Google Ads click, campaign, first page) so each inquiry email shows where the lead came from.
  var lead = {};
  try {
    lead = JSON.parse(sessionStorage.getItem('plg_lead') || '{}');
    if (!lead.landing) {
      var q = new URLSearchParams(location.search);
      var paid = q.get('gclid') || q.get('gbraid') || q.get('wbraid');
      var ref = document.referrer && document.referrer.indexOf(location.hostname) === -1 ? document.referrer.split('/')[2] : '';
      lead = { landing: location.pathname, source: paid ? 'Google Ads' : (q.get('utm_source') || ref || 'Direct'),
               campaign: q.get('utm_campaign') || '', keyword: q.get('utm_term') || '' };
      sessionStorage.setItem('plg_lead', JSON.stringify(lead));
    }
  } catch (e) {}
  function addHidden(form, name, value) {
    if (!value) return;
    var el = form.querySelector('input[name="' + name + '"]');
    if (!el) { el = document.createElement('input'); el.type = 'hidden'; el.name = name; form.appendChild(el); }
    el.value = value;
  }
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
      addHidden(form, 'lead_source', lead.source); addHidden(form, 'ad_campaign', lead.campaign); addHidden(form, 'ad_keyword', lead.keyword);
      addHidden(form, 'first_page', lead.landing); addHidden(form, 'from_site', location.hostname);
      fetch(ENDPOINT, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (String(d.success) !== 'true') throw new Error(d.message || 'failed');
          form.reset(); status.textContent = form.dataset.ok; status.className = 'form-status ok';
          if (window.gtag) { gtag('event', 'generate_lead', { method: 'website_form' }); gtag('event', 'conversion', { send_to: 'AW-18436695999/HN4qCJOr1rsdEL_PptdE' }); }
        })
        .catch(function () { status.textContent = form.dataset.err; status.className = 'form-status err'; })
        .finally(function () { btn.disabled = false; });
    });
  });
  // Track phone and text clicks as conversions when Google tags are installed.
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="tel:"], a[href^="sms:"]');
    if (a && window.gtag) { gtag('event', a.href.indexOf('tel:') === 0 ? 'phone_click' : 'text_click'); gtag('event', 'conversion', { send_to: 'AW-18436695999/4bMFCPSy3bsdEL_PptdE' }); }
  });
  // Hide the sticky call bar while someone is typing in the form, so it never covers the fields or the Send button.
  document.addEventListener('focusin', function (e) { if (e.target.closest && e.target.closest('.case-form')) document.body.classList.add('typing'); });
  document.addEventListener('focusout', function (e) { if (e.target.closest && e.target.closest('.case-form')) document.body.classList.remove('typing'); });
  // Close the mobile menu when a link is chosen.
  document.querySelectorAll('.nav-mobile a').forEach(function (a) {
    a.addEventListener('click', function () { var d = a.closest('details'); if (d) d.removeAttribute('open'); });
  });
})();

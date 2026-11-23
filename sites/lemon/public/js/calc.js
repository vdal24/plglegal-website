// Lemon law buyback estimator. Runs entirely in the browser; nothing is sent anywhere.
(function () {
  var f = document.getElementById('bb-calc');
  if (!f) return;
  var $ = function (n) { return f.querySelector('[name="' + n + '"]'); };
  var num = function (n) { var v = parseFloat(String($(n).value).replace(/[^0-9.]/g, '')); return isNaN(v) ? 0 : v; };
  var usd = function (v) { return '$' + Math.round(v).toLocaleString('en-US'); };
  var out = function (k, v) { var el = f.querySelector('[data-out="' + k + '"]'); if (el) el.textContent = v; };

  function money(el) {
    var raw = el.value.replace(/[^0-9.]/g, '');
    if (!raw) { el.value = ''; return; }
    var parts = raw.split('.');
    el.value = Number(parts[0]).toLocaleString('en-US') + (parts.length > 1 ? '.' + parts[1].slice(0, 2) : '');
  }

  function calc() {
    var price = num('price'), fees = num('fees'), fin = num('finance'), inc = num('incidentals');
    var m0 = num('miles_start'), m1 = num('miles_repair'), owed = num('owed');
    var used = Math.max(0, m1 - m0);
    var offset = price * used / 120000;
    var total = Math.max(0, price + fees + fin + inc - offset);
    var lender = Math.min(owed, total);
    var you = Math.max(0, total - lender);
    out('total', price ? usd(total) : '$0');
    out('offset', used ? '- ' + usd(offset) : '$0');
    out('paid', usd(price + fees + fin + inc));
    out('lender', usd(lender));
    out('you', usd(you));
    f.classList.toggle('has-loan', owed > 0);
    f.classList.toggle('has-value', price > 0);
  }

  f.addEventListener('input', function (e) {
    if (e.target.dataset.money !== undefined) money(e.target);
    calc();
  });
  f.addEventListener('submit', function (e) { e.preventDefault(); calc(); });
  calc();
})();

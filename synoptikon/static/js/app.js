// Algemeen: thema-schakelaar en bevestigingsdialogen. Geen afhankelijkheden.
(function () {
  var root = document.documentElement;
  var knop = document.getElementById('thema-knop');
  function huidig() {
    var t = root.dataset.theme;
    if (t === 'auto' || !t) return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    return t;
  }
  if (knop) {
    knop.addEventListener('click', function () {
      var nieuw = huidig() === 'dark' ? 'light' : 'dark';
      root.dataset.theme = nieuw;
      try { localStorage.setItem('thema', nieuw); } catch (e) {}
    });
  }
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (f.dataset && f.dataset.bevestig && !window.confirm(f.dataset.bevestig)) e.preventDefault();
  });
  // Formulieren die bij wijziging direct verzenden (filters, keuzelijsten).
  document.addEventListener('change', function (e) {
    var el = e.target;
    if (el.matches && el.matches('select.auto-submit') && el.form) el.form.submit();
    // Stelselkeuze → taalveld invullen en systematiek-opties filteren.
    if (el.matches && el.matches('select[name="stelsel_code"]')) {
      var opt = el.selectedOptions[0], form = el.form;
      if (!form || !opt) return;
      var taal = form.querySelector('input[name="taal"]');
      if (taal && opt.dataset.taal) { if (taal.classList.contains('taal-veld')) taal.placeholder = opt.dataset.taal; else taal.value = opt.dataset.taal; }
      filterSystematiek(form, el.value);
    }
  });
  function filterSystematiek(form, code) {
    var sys = form.querySelector('select[name="systematiek_id"]');
    if (!sys) return;
    Array.prototype.forEach.call(sys.options, function (o) { if (o.value) o.hidden = o.dataset.stelsel !== code; });
    if (sys.selectedOptions[0] && sys.selectedOptions[0].hidden) sys.value = '';
  }
  document.querySelectorAll('form select[name="stelsel_code"]').forEach(function (s) { filterSystematiek(s.form, s.value); });
  // Sluit open menu's bij klik erbuiten.
  document.addEventListener('click', function (e) {
    document.querySelectorAll('details.menu[open]').forEach(function (d) { if (!d.contains(e.target)) d.removeAttribute('open'); });
  });
  // Systematiek: artikeltekst pas ophalen als een knoop wordt opengeklapt.
  function laadTekst(d) {
    var boom = d.closest('[data-lees]');
    if (!boom || !d.dataset.k || d.dataset.geladen) return;
    d.dataset.geladen = '1';
    var doel = d.querySelector('.sys-artikelen');
    doel.textContent = '…';
    fetch(boom.dataset.lees + d.dataset.k + '?fragment=1', { credentials: 'same-origin' }).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.text();
    }).then(function (html) {
      doel.innerHTML = html;
      var a = d.dataset.artikel && document.getElementById(d.dataset.artikel);
      if (a) { a.classList.add('gezocht-artikel'); a.scrollIntoView({ block: 'start' }); }
    }).catch(function () { delete d.dataset.geladen; doel.textContent = ''; });
  }
  document.addEventListener('toggle', function (e) {
    if (e.target.matches && e.target.matches('details.sys-tekst') && e.target.open) laadTekst(e.target);
  }, true);
  document.querySelectorAll('details.sys-tekst[open]').forEach(laadTekst);
  // #knoop-123: het pad naar die knoop openklappen.
  function openHash() {
    var m = /^#knoop-\d+$/.test(location.hash) && document.getElementById(location.hash.slice(1));
    if (!m) return;
    for (var p = m; p; p = p.parentElement) if (p.tagName === 'DETAILS') p.open = true;
    var eigen = m.querySelector(':scope > details');
    if (eigen) eigen.open = true;
    m.scrollIntoView({ block: 'start' });
  }
  openHash();
  window.addEventListener('hashchange', openHash);
})();

// Stelselkiezer (/profiel, /welkom): zoeken over alle regio's, 'alles in deze regio', telling per regio.
(function () {
  document.querySelectorAll('[data-stelselkiezer]').forEach(function (form) {
    var zoek = form.querySelector('.kiezer-zoek');
    var regios = Array.prototype.slice.call(form.querySelectorAll('.kiezer-regio'));
    var dicht = {};
    function tel(r) {
      var vakjes = r.querySelectorAll('input[type=checkbox]');
      var n = r.querySelectorAll('input[type=checkbox]:checked').length;
      var t = r.querySelector('[data-telling]');
      if (t) t.textContent = t.textContent.replace(/^\d+/, n);
      var knop = r.querySelector('.kiezer-alles');
      if (knop) knop.dataset.aan = n === vakjes.length ? '1' : '';
    }
    zoek.hidden = false;
    zoek.addEventListener('input', function () {
      var q = zoek.value.trim().toLowerCase();
      regios.forEach(function (r, i) {
        if (!(i in dicht)) dicht[i] = !r.open;
        var raak = 0;
        r.querySelectorAll('li[data-zoek]').forEach(function (li) {
          var ja = !q || li.dataset.zoek.indexOf(q) >= 0;
          li.hidden = !ja; if (ja) raak++;
        });
        r.hidden = q && !raak;
        r.open = q ? raak > 0 : !dicht[i];
      });
      if (!q) dicht = {};
    });
    regios.forEach(function (r) {
      var knop = r.querySelector('.kiezer-alles');
      knop.hidden = false;
      knop.addEventListener('click', function () {
        var aan = knop.dataset.aan !== '1';
        r.querySelectorAll('li:not([hidden]) input[type=checkbox]').forEach(function (cb) { cb.checked = aan; });
        tel(r);
      });
      r.addEventListener('change', function () { tel(r); });
      tel(r);
    });
  });
})();

// Begrippenkaart: krachtgestuurde graaf in SVG, zonder bibliotheek.
// Stelsels liggen op een ring, per rechtsfamilie aaneengesloten; Europees en
// eenvormig recht staat in het midden. Elke vraag (cluster) krijgt een eigen
// ring: de eerste binnen, de volgende daarbuiten. Elk begrip wordt naar het anker van zijn
// stelsel getrokken, relaties trekken begrippen over de ring naar elkaar toe.
// Tikken op een begrip toont alleen zijn buren; slepen verschuift, knijpen of
// scrollen zoomt, een begrip slepen verplaatst het.
(function () {
  var svg = document.getElementById('kaart');
  var dataEl = document.getElementById('kaart-data');
  var paneel = document.getElementById('kaart-paneel');
  if (!svg || !dataEl) return;
  var data = JSON.parse(dataEl.textContent);
  var NS = 'http://www.w3.org/2000/svg';
  var FAMILIES = ['romaans', 'gemengd', 'germaans', 'nordisch', 'common_law', 'overig', 'supranationaal'];
  // Teksten in de taal van de pagina (begrippenkaart.html, #kaart-i18n); Nederlands als terugval.
  var T = {};
  try { T = JSON.parse(document.getElementById('kaart-i18n').textContent) || {}; } catch (e) {}
  function t(s) { return T[s] || s; }
  var LABEL = { faux_ami: t('faux ami'), geen: t('geen equivalent'), deels: t('deels'), equivalent: t('equivalent') };

  if (!data.knopen.length) {
    svg.outerHTML = '<p class="stil" style="padding:1rem">' + t('Nog geen begrippen.') + '</p>';
    return;
  }

  // Logisch canvas groeit mee met het aantal begrippen; het beeld zoomt.
  var S = Math.max(800, Math.sqrt(data.knopen.length) * 165);
  var CX = S / 2, CY = S / 2, R = S * 0.4;

  // Clusters: de eerste vraag van een begrip; zonder vraag op de middelste ring.
  var clusters = [];
  data.knopen.forEach(function (k) { var c = (k.vragen || [])[0] || ''; if (c && clusters.indexOf(c) < 0) clusters.push(c); });
  clusters.sort();
  function straal(k) {
    var c = (k.vragen || [])[0] || '';
    if (clusters.length < 2 || !c) return R;
    return R * (0.62 + 0.5 * clusters.indexOf(c) / (clusters.length - 1));
  }

  // Ankers: stelsels op volgorde van familie rond de ring, supranationaal in het midden.
  var stelsels = [];
  data.knopen.forEach(function (k) { if (stelsels.indexOf(k.stelsel) < 0) stelsels.push(k.stelsel); });
  var familieVan = {};
  data.knopen.forEach(function (k) { familieVan[k.stelsel] = k.familie; });
  stelsels.sort(function (a, b) { return FAMILIES.indexOf(familieVan[a]) - FAMILIES.indexOf(familieVan[b]); });
  var ring = stelsels.filter(function (s) { return familieVan[s] !== 'supranationaal'; });
  var anker = {};
  ring.forEach(function (s, i) {
    var hoek = -Math.PI / 2 + (i / Math.max(1, ring.length)) * Math.PI * 2;
    anker[s] = { x: CX + Math.cos(hoek) * R, y: CY + Math.sin(hoek) * R, hoek: hoek };
  });
  stelsels.forEach(function (s) { if (!anker[s]) anker[s] = { x: CX, y: CY, hoek: null }; });

  // Stelsels die niet bij mijn stelsels horen staan onder 'meer stelsels…' en beginnen uitgevinkt.
  var uit = {};
  document.querySelectorAll('input[data-stelsel]').forEach(function (cb) { if (!cb.checked) uit[cb.dataset.stelsel] = true; });
  var knopen = data.knopen.map(function (k, i) {
    var a = anker[k.stelsel], r = straal(k);
    var doel = a.hoek === null ? { x: CX, y: CY + (r - R) * 0.6 } : { x: CX + Math.cos(a.hoek) * r, y: CY + Math.sin(a.hoek) * r };
    return Object.assign({}, k, { doel: doel, x: doel.x + Math.cos(i * 2.4) * 30, y: doel.y + Math.sin(i * 2.4) * 30, vx: 0, vy: 0, zichtbaar: !uit[k.stelsel] });
  });
  var perId = {}; knopen.forEach(function (k) { perId[k.id] = k; });
  var kanten = data.kanten.filter(function (e) { return perId[e.van] && perId[e.naar]; }).map(function (e) {
    return Object.assign({}, e, { a: perId[e.van], b: perId[e.naar] });
  });

  var g_wereld = document.createElementNS(NS, 'g');
  var g_ankers = document.createElementNS(NS, 'g'), g_kanten = document.createElementNS(NS, 'g'), g_labels = document.createElementNS(NS, 'g'), g_knopen = document.createElementNS(NS, 'g');
  [g_ankers, g_kanten, g_labels, g_knopen].forEach(function (g) { g_wereld.appendChild(g); });
  svg.appendChild(g_wereld);

  // Stelselnamen buiten de ring.
  stelsels.forEach(function (s) {
    var a = anker[s];
    var t = document.createElementNS(NS, 'text');
    t.setAttribute('class', 'anker fam-' + familieVan[s]);
    t.setAttribute('text-anchor', 'middle');
    var r = a.hoek === null ? 0 : R * 1.12 + S * 0.05;
    t.setAttribute('x', a.hoek === null ? CX : CX + Math.cos(a.hoek) * r);
    t.setAttribute('y', a.hoek === null ? CY - S * 0.08 : CY + Math.sin(a.hoek) * r);
    t.textContent = s;
    g_ankers.appendChild(t);
    a.el = t;
  });

  function tekstbreedte(t) { return Math.min(260, Math.max(48, t.length * 7.4 + 22)); }

  kanten.forEach(function (e) {
    e.el = document.createElementNS(NS, 'line'); e.el.setAttribute('class', 'kant rel-' + e.type); g_kanten.appendChild(e.el);
    e.lbl = document.createElementNS(NS, 'text'); e.lbl.setAttribute('class', 'kant-label rel-' + e.type);
    e.lbl.textContent = LABEL[e.type] || e.type;
    g_labels.appendChild(e.lbl);
  });
  knopen.forEach(function (k) {
    var term = k.term.length > 34 ? k.term.slice(0, 32) + '…' : k.term;
    k.w = tekstbreedte(term); k.h = 34;
    k.buren = [];
    k.el = document.createElementNS(NS, 'g'); k.el.setAttribute('class', 'knoop fam-' + k.familie);
    var r = document.createElementNS(NS, 'rect'); r.setAttribute('width', k.w); r.setAttribute('height', k.h); r.setAttribute('x', -k.w / 2); r.setAttribute('y', -k.h / 2);
    var balk = document.createElementNS(NS, 'rect'); balk.setAttribute('class', 'balk'); balk.setAttribute('width', 4); balk.setAttribute('height', k.h); balk.setAttribute('x', -k.w / 2); balk.setAttribute('y', -k.h / 2);
    var t = document.createElementNS(NS, 'text'); t.setAttribute('text-anchor', 'middle'); t.setAttribute('y', 6); t.textContent = term;
    var c = document.createElementNS(NS, 'text'); c.setAttribute('class', 'code'); c.setAttribute('x', -k.w / 2 + 8); c.setAttribute('y', -k.h / 2 + 10); c.textContent = k.stelsel;
    var titel = document.createElementNS(NS, 'title'); titel.textContent = k.stelsel + ' · ' + k.term;
    k.el.appendChild(r); k.el.appendChild(balk); k.el.appendChild(t); k.el.appendChild(c); k.el.appendChild(titel); g_knopen.appendChild(k.el);
  });
  kanten.forEach(function (e) {
    e.a.buren.push(e.b); e.b.buren.push(e.a);
    if (e.type === 'faux_ami') { e.a.el.classList.add('faux'); e.b.el.classList.add('faux'); }
  });

  // --- simulatie ---------------------------------------------------------------------
  var alpha = 1, bezig = false, sleepKnoop = null;
  function stap() {
    var i, j, a, b, dx, dy, d, f;
    for (i = 0; i < knopen.length; i++) {
      a = knopen[i]; if (!a.zichtbaar) continue;
      for (j = i + 1; j < knopen.length; j++) {
        b = knopen[j]; if (!b.zichtbaar) continue;
        dx = b.x - a.x; dy = b.y - a.y;
        var ox = (a.w + b.w) / 2 + 14 - Math.abs(dx), oy = (a.h + b.h) / 2 + 10 - Math.abs(dy);
        d = Math.sqrt(dx * dx + dy * dy) || 1;
        f = 2600 / (d * d);
        if (ox > 0 && oy > 0) f += Math.min(ox, oy) * 0.12;  // overlap: harder duwen
        dx /= d; dy /= d;
        a.vx -= dx * f; a.vy -= dy * f; b.vx += dx * f; b.vy += dy * f;
      }
      a.vx += (a.doel.x - a.x) * 0.05; a.vy += (a.doel.y - a.y) * 0.05;
    }
    kanten.forEach(function (e) {
      if (!e.a.zichtbaar || !e.b.zichtbaar) return;
      dx = e.b.x - e.a.x; dy = e.b.y - e.a.y; d = Math.sqrt(dx * dx + dy * dy) || 1;
      var doel = e.type === 'equivalent' ? S * 0.14 : S * 0.2;
      f = (d - doel) * 0.0005; dx /= d; dy /= d;
      e.a.vx += dx * f; e.a.vy += dy * f; e.b.vx -= dx * f; e.b.vy -= dy * f;
    });
    knopen.forEach(function (k) {
      if (k.vast) { k.vx = k.vy = 0; return; }
      k.vx *= 0.8; k.vy *= 0.8;
      k.x += k.vx * alpha; k.y += k.vy * alpha;
    });
    alpha = Math.max(0.02, alpha * 0.985);
  }
  function lus() {
    stap(); teken();
    if (alpha > 0.021 || sleepKnoop) requestAnimationFrame(lus); else bezig = false;
  }
  function wek(sterkte) { alpha = Math.max(alpha, sterkte || 0.4); if (!bezig) { bezig = true; requestAnimationFrame(lus); } }

  function teken() {
    knopen.forEach(function (k) { k.el.setAttribute('transform', 'translate(' + k.x.toFixed(1) + ',' + k.y.toFixed(1) + ')'); k.el.style.display = k.zichtbaar ? '' : 'none'; });
    kanten.forEach(function (e) {
      var zicht = e.a.zichtbaar && e.b.zichtbaar;
      e.el.style.display = zicht ? '' : 'none';
      e.lbl.style.display = zicht && e.toon ? '' : 'none';
      if (!zicht) return;
      e.el.setAttribute('x1', e.a.x); e.el.setAttribute('y1', e.a.y); e.el.setAttribute('x2', e.b.x); e.el.setAttribute('y2', e.b.y);
      e.lbl.setAttribute('x', (e.a.x + e.b.x) / 2); e.lbl.setAttribute('y', (e.a.y + e.b.y) / 2 - 5);
    });
    stelsels.forEach(function (s) { anker[s].el.style.display = knopen.some(function (k) { return k.stelsel === s && k.zichtbaar; }) ? '' : 'none'; });
  }

  // Vooraf uitrekenen, zodat de kaart meteen rustig staat.
  for (var n = 0; n < 320; n++) stap();
  alpha = 0.05;

  // --- beeld: verschuiven en zoomen via de viewBox -------------------------------------------
  var vb = { x: 0, y: 0, w: S, h: S };
  function zetBeeld() { svg.setAttribute('viewBox', vb.x + ' ' + vb.y + ' ' + vb.w + ' ' + vb.h); }
  // Op een smal scherm ligt het paneel over de onderste helft: dan past de focus in de bovenste.
  function smal() { return window.matchMedia('(max-width: 700px)').matches; }
  function passend(alleen) {
    var lijst = (alleen || knopen).filter(function (k) { return k.zichtbaar; });
    if (!lijst.length) return;
    var x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    lijst.forEach(function (k) { x0 = Math.min(x0, k.x - k.w / 2); x1 = Math.max(x1, k.x + k.w / 2); y0 = Math.min(y0, k.y - k.h / 2); y1 = Math.max(y1, k.y + k.h / 2); });
    if (!alleen) stelsels.forEach(function (s) {
      var el = anker[s].el; if (el.style.display === 'none') return;
      var x = +el.getAttribute('x'), y = +el.getAttribute('y');
      x0 = Math.min(x0, x - 20); x1 = Math.max(x1, x + 20); y0 = Math.min(y0, y - 24); y1 = Math.max(y1, y + 6);
    });
    var marge = 30, bw = x1 - x0 + 2 * marge, bh = y1 - y0 + 2 * marge;
    var vw = svg.clientWidth || 900, vh = svg.clientHeight || 600;
    var boven = alleen && smal() && !paneel.hidden ? 0.45 : 1;  // deel van de hoogte dat zichtbaar blijft
    var schaal = Math.max(bw / vw, bh / (vh * boven), 0.6);  // niet verder inzoomen dan 1/0,6
    vb.w = vw * schaal; vb.h = vh * schaal;
    vb.x = (x0 + x1) / 2 - vb.w / 2; vb.y = (y0 + y1) / 2 - vb.h * boven / 2;
    zetBeeld();
  }
  function zoom(factor, px, py) {
    var nw = Math.min(S * 3, Math.max(200, vb.w * factor)), f = nw / vb.w;
    if (px === undefined) { px = vb.x + vb.w / 2; py = vb.y + vb.h / 2; }
    vb.x = px - (px - vb.x) * f; vb.y = py - (py - vb.y) * f; vb.w *= f; vb.h *= f;
    zetBeeld();
  }
  function svgPunt(cx, cy) {
    var r = svg.getBoundingClientRect();
    return { x: vb.x + (cx - r.left) / r.width * vb.w, y: vb.y + (cy - r.top) / r.height * vb.h };
  }

  svg.addEventListener('wheel', function (ev) {
    ev.preventDefault();
    var p = svgPunt(ev.clientX, ev.clientY);
    zoom(ev.deltaY > 0 ? 1.12 : 1 / 1.12, p.x, p.y);
  }, { passive: false });

  // Pointers: één vinger verschuift (of sleept een begrip), twee vingers zoomen.
  var pointers = {}, pan = null, knijp = null, bewogen = false;
  function aantal() { return Object.keys(pointers).length; }
  svg.addEventListener('pointerdown', function (ev) {
    pointers[ev.pointerId] = { x: ev.clientX, y: ev.clientY };
    svg.setPointerCapture(ev.pointerId);
    bewogen = false;
    if (aantal() === 2) {
      var ps = Object.keys(pointers).map(function (k) { return pointers[k]; });
      knijp = { d: Math.hypot(ps[0].x - ps[1].x, ps[0].y - ps[1].y), w: vb.w };
      pan = null; if (sleepKnoop) { sleepKnoop.vast = false; sleepKnoop = null; }
      return;
    }
    var k = knoopBij(ev.target);
    if (k) { sleepKnoop = k; k.vast = true; }
    else pan = { x: ev.clientX, y: ev.clientY, vx: vb.x, vy: vb.y };
  });
  svg.addEventListener('pointermove', function (ev) {
    if (!pointers[ev.pointerId]) return;
    var oud = pointers[ev.pointerId];
    if (Math.abs(ev.clientX - oud.x) + Math.abs(ev.clientY - oud.y) > 3) bewogen = true;
    pointers[ev.pointerId] = { x: ev.clientX, y: ev.clientY };
    if (knijp && aantal() === 2) {
      var ps = Object.keys(pointers).map(function (k) { return pointers[k]; });
      var d = Math.hypot(ps[0].x - ps[1].x, ps[0].y - ps[1].y) || 1;
      var m = svgPunt((ps[0].x + ps[1].x) / 2, (ps[0].y + ps[1].y) / 2);
      zoom((knijp.w * knijp.d / d) / vb.w, m.x, m.y);
      return;
    }
    if (sleepKnoop && bewogen) {
      var p = svgPunt(ev.clientX, ev.clientY); sleepKnoop.x = p.x; sleepKnoop.y = p.y; wek(0.3);
    } else if (pan) {
      var r = svg.getBoundingClientRect();
      vb.x = pan.vx - (ev.clientX - pan.x) / r.width * vb.w;
      vb.y = pan.vy - (ev.clientY - pan.y) / r.height * vb.h;
      zetBeeld();
    }
  });
  function los(ev) {
    var k = sleepKnoop, klik = !bewogen && !knijp;
    delete pointers[ev.pointerId];
    if (aantal() < 2) knijp = null;
    if (sleepKnoop) { sleepKnoop.vast = false; sleepKnoop = null; }
    pan = null;
    if (ev.type !== 'pointerup' || !klik) return;
    if (k) { focus(k); if (smal()) passend([k].concat(k.buren)); } else wis();
  }
  svg.addEventListener('pointerup', los);
  svg.addEventListener('pointercancel', los);

  function knoopBij(el) {
    while (el && el !== svg) {
      if (el.classList && el.classList.contains('knoop')) return knopen.find(function (k) { return k.el === el; });
      el = el.parentNode;
    }
    return null;
  }

  // --- focus en detailpaneel --------------------------------------------------------
  function focus(k) {
    svg.classList.add('gefocust');
    knopen.forEach(function (n) {
      n.el.classList.toggle('actief', n === k);
      n.el.classList.toggle('buur', k.buren.indexOf(n) >= 0);
    });
    kanten.forEach(function (e) {
      e.toon = e.a === k || e.b === k;
      e.el.classList.toggle('buur', e.toon);
      e.lbl.classList.toggle('buur', e.toon);
    });
    teken();
    toon(k);
  }
  function wis() {
    svg.classList.remove('gefocust');
    knopen.forEach(function (n) { n.el.classList.remove('actief', 'buur'); });
    kanten.forEach(function (e) { e.toon = false; e.el.classList.remove('buur'); e.lbl.classList.remove('buur'); });
    teken();
    paneel.hidden = true;
  }
  function toon(k) {
    var rel = kanten.filter(function (e) { return e.a === k || e.b === k; }).map(function (e) {
      var ander = e.a === k ? e.b : e.a;
      return '<li><span class="relatie rel-' + e.type + '">' + esc(e.label) + '</span> <a href="/begrippen/' + ander.id + '" data-knoop="' + ander.id + '"><span class="stelsel-code">' + ander.stelsel + '</span> ' + esc(ander.term) + '</a>' + (e.toelichting ? '<div class="toelichting">' + esc(e.toelichting) + '</div>' : '') + '</li>';
    }).join('');
    paneel.innerHTML = '<button type="button" class="knop-tekst sluit" aria-label="' + t('Sluiten') + '">×</button>' +
      '<p class="kruimel">' + esc(k.stelsel) + ' · ' + esc(k.taal) + '</p><h3 class="serif">' + esc(k.term) + '</h3>' +
      (k.vindplaats ? '<p class="stil klein">' + esc(k.vindplaats) + '</p>' : '') +
      (k.definitie ? '<p>' + esc(k.definitie) + '</p>' : '') +
      (rel ? '<ul class="relatielijst">' + rel + '</ul>' : '<p class="stil">' + t('Geen relaties.') + '</p>') +
      '<p><a class="knop klein" href="/begrippen/' + k.id + '">' + t('Open begrip') + '</a></p>';
    paneel.hidden = false;
    paneel.scrollTop = 0;
    paneel.querySelector('.sluit').addEventListener('click', wis);
    // Een buur in het paneel aantikken verplaatst de focus, in plaats van weg te navigeren.
    paneel.querySelectorAll('a[data-knoop]').forEach(function (a) {
      a.addEventListener('click', function (ev) {
        var n = perId[a.dataset.knoop];
        if (!n || !n.zichtbaar) return;
        ev.preventDefault(); focus(n); passend([n].concat(n.buren));
      });
    });
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  // --- filters en knoppen ---------------------------------------------------------------
  var vakjes = Array.prototype.slice.call(document.querySelectorAll('input[data-stelsel]'));
  function pasFilterToe() {
    var aan = {}; vakjes.forEach(function (cb) { aan[cb.dataset.stelsel] = cb.checked; });
    knopen.forEach(function (k) { k.zichtbaar = aan[k.stelsel] !== false; });
    wis(); wek(0.3); passend();
  }
  vakjes.forEach(function (cb) { cb.addEventListener('change', pasFilterToe); });
  document.querySelectorAll('.kaart-stelsels .familie-knop').forEach(function (knop) {
    knop.addEventListener('click', function () {
      var groep = knop.closest('.familie-groep');
      var eigen = Array.prototype.slice.call(groep.querySelectorAll('input[data-stelsel]'));
      var allesAan = eigen.every(function (cb) { return cb.checked; });
      eigen.forEach(function (cb) { cb.checked = !allesAan; });
      pasFilterToe();
    });
  });
  document.querySelectorAll('[data-zoom]').forEach(function (knop) {
    knop.addEventListener('click', function () {
      var z = knop.dataset.zoom;
      if (z === 'in') zoom(1 / 1.3); else if (z === 'uit') zoom(1.3); else passend();
    });
  });
  window.addEventListener('resize', function () { passend(); });

  if (smal()) document.querySelectorAll('.kaart-filter').forEach(function (d) { d.open = false; });
  teken();
  // ?begrip=<id>: meteen op dat begrip en zijn buren inzoomen.
  var gevraagd = perId[new URLSearchParams(location.search).get('begrip')];
  if (gevraagd) { focus(gevraagd); passend([gevraagd].concat(gevraagd.buren)); } else passend();
})();

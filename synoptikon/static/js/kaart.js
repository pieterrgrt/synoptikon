// Begrippenkaart: eenvoudige krachtgestuurde graaf in SVG, zonder bibliotheek.
// Knopen zijn begrippen, gekleurd per relatie-type van hun kanten; faux amis en
// "geen equivalent" krijgen afwijkende lijnen en knooprandjes.
(function () {
  var svg = document.getElementById('kaart');
  var dataEl = document.getElementById('kaart-data');
  var paneel = document.getElementById('kaart-paneel');
  if (!svg || !dataEl) return;
  var data = JSON.parse(dataEl.textContent);
  var NS = 'http://www.w3.org/2000/svg';

  var W = svg.clientWidth || 900, H = svg.clientHeight || 600;
  svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);

  var knopen = data.knopen.map(function (k, i) {
    var hoek = (i / Math.max(1, data.knopen.length)) * Math.PI * 2;
    return Object.assign({}, k, { x: W / 2 + Math.cos(hoek) * Math.min(W, H) * 0.3, y: H / 2 + Math.sin(hoek) * Math.min(W, H) * 0.3, vx: 0, vy: 0, zichtbaar: true });
  });
  var perId = {}; knopen.forEach(function (k) { perId[k.id] = k; });
  var kanten = data.kanten.filter(function (e) { return perId[e.van] && perId[e.naar]; }).map(function (e) {
    return Object.assign({}, e, { a: perId[e.van], b: perId[e.naar] });
  });

  // Begrippen uit hetzelfde stelsel groeperen we zacht rond een eigen hoek, zodat
  // de stelsels als kolommen herkenbaar blijven.
  var stelsels = []; knopen.forEach(function (k) { if (stelsels.indexOf(k.stelsel) < 0) stelsels.push(k.stelsel); });
  var anker = {};
  stelsels.forEach(function (s, i) {
    var x = stelsels.length > 1 ? (W * (i + 0.5)) / stelsels.length : W / 2;
    anker[s] = { x: x, y: H / 2 };
  });

  var g_kanten = document.createElementNS(NS, 'g'), g_labels = document.createElementNS(NS, 'g'), g_knopen = document.createElementNS(NS, 'g');
  svg.appendChild(g_kanten); svg.appendChild(g_labels); svg.appendChild(g_knopen);

  function tekstbreedte(t, grootte) { return Math.max(40, t.length * grootte * 0.55 + 20); }

  kanten.forEach(function (e) {
    e.el = document.createElementNS(NS, 'line'); e.el.setAttribute('class', 'kant rel-' + e.type); g_kanten.appendChild(e.el);
    e.lbl = document.createElementNS(NS, 'text'); e.lbl.setAttribute('class', 'kant-label rel-' + e.type);
    e.lbl.textContent = { faux_ami: 'faux ami', geen: 'geen equivalent', deels: 'deels', equivalent: 'equivalent' }[e.type] || e.type;
    g_labels.appendChild(e.lbl);
  });
  knopen.forEach(function (k) {
    k.w = tekstbreedte(k.term, 14); k.h = 36;
    var faux = kanten.some(function (e) { return e.type === 'faux_ami' && (e.a === k || e.b === k); });
    var geen = kanten.some(function (e) { return e.type === 'geen' && (e.a === k || e.b === k); });
    k.el = document.createElementNS(NS, 'g'); k.el.setAttribute('class', 'knoop' + (faux ? ' faux' : '') + (geen ? ' geen' : ''));
    var r = document.createElementNS(NS, 'rect'); r.setAttribute('width', k.w); r.setAttribute('height', k.h); r.setAttribute('x', -k.w / 2); r.setAttribute('y', -k.h / 2);
    var t = document.createElementNS(NS, 'text'); t.setAttribute('text-anchor', 'middle'); t.setAttribute('y', 6); t.textContent = k.term;
    var c = document.createElementNS(NS, 'text'); c.setAttribute('class', 'code'); c.setAttribute('x', -k.w / 2 + 6); c.setAttribute('y', -k.h / 2 + 11); c.textContent = k.stelsel;
    k.el.appendChild(r); k.el.appendChild(t); k.el.appendChild(c); g_knopen.appendChild(k.el);
    k.el.addEventListener('click', function (ev) { ev.stopPropagation(); toon(k); });
  });

  // Simulatie
  var alpha = 1, bezig = true;
  function stap() {
    var i, j, a, b, dx, dy, d, f;
    for (i = 0; i < knopen.length; i++) {
      a = knopen[i]; if (!a.zichtbaar) continue;
      for (j = i + 1; j < knopen.length; j++) {
        b = knopen[j]; if (!b.zichtbaar) continue;
        dx = b.x - a.x; dy = b.y - a.y; d = Math.sqrt(dx * dx + dy * dy) || 1;
        var min = (a.w + b.w) / 2 + 30;
        f = (d < min ? (min - d) * 0.08 : 0) + 1800 / (d * d);
        dx /= d; dy /= d;
        a.vx -= dx * f; a.vy -= dy * f; b.vx += dx * f; b.vy += dy * f;
      }
      var an = anker[a.stelsel];
      a.vx += (an.x - a.x) * 0.004; a.vy += (an.y - a.y) * 0.002;
      a.vx += (W / 2 - a.x) * 0.0005; a.vy += (H / 2 - a.y) * 0.0005;
    }
    kanten.forEach(function (e) {
      if (!e.a.zichtbaar || !e.b.zichtbaar) return;
      dx = e.b.x - e.a.x; dy = e.b.y - e.a.y; d = Math.sqrt(dx * dx + dy * dy) || 1;
      var doel = e.type === 'geen' ? 220 : (e.type === 'equivalent' ? 130 : 160);
      f = (d - doel) * 0.01; dx /= d; dy /= d;
      e.a.vx += dx * f; e.a.vy += dy * f; e.b.vx -= dx * f; e.b.vy -= dy * f;
    });
    knopen.forEach(function (k) {
      if (k.vast) { k.vx = k.vy = 0; return; }
      k.vx *= 0.82; k.vy *= 0.82;
      k.x = Math.max(k.w / 2 + 4, Math.min(W - k.w / 2 - 4, k.x + k.vx * alpha));
      k.y = Math.max(k.h / 2 + 4, Math.min(H - k.h / 2 - 4, k.y + k.vy * alpha));
    });
    alpha = Math.max(0.02, alpha * 0.985);
    teken();
    if (alpha > 0.021 || sleep) requestAnimationFrame(stap); else bezig = false;
  }
  function wek() { alpha = Math.max(alpha, 0.6); if (!bezig) { bezig = true; requestAnimationFrame(stap); } }
  function teken() {
    knopen.forEach(function (k) { k.el.setAttribute('transform', 'translate(' + k.x + ',' + k.y + ')'); k.el.style.display = k.zichtbaar ? '' : 'none'; });
    kanten.forEach(function (e) {
      var zicht = e.a.zichtbaar && e.b.zichtbaar;
      e.el.style.display = e.lbl.style.display = zicht ? '' : 'none';
      if (!zicht) return;
      e.el.setAttribute('x1', e.a.x); e.el.setAttribute('y1', e.a.y); e.el.setAttribute('x2', e.b.x); e.el.setAttribute('y2', e.b.y);
      e.lbl.setAttribute('x', (e.a.x + e.b.x) / 2); e.lbl.setAttribute('y', (e.a.y + e.b.y) / 2 - 5);
    });
  }

  // Slepen van knopen (pointer events)
  var sleep = null;
  function svgPunt(ev) { var p = svg.createSVGPoint(); p.x = ev.clientX; p.y = ev.clientY; return p.matrixTransform(svg.getScreenCTM().inverse()); }
  knopen.forEach(function (k) {
    k.el.addEventListener('pointerdown', function (ev) { sleep = k; k.vast = true; k.el.setPointerCapture(ev.pointerId); wek(); });
  });
  svg.addEventListener('pointermove', function (ev) { if (!sleep) return; var p = svgPunt(ev); sleep.x = p.x; sleep.y = p.y; wek(); });
  function los() { if (sleep) { sleep.vast = false; sleep = null; wek(); } }
  svg.addEventListener('pointerup', los); svg.addEventListener('pointercancel', los);

  // Detailpaneel
  function toon(k) {
    knopen.forEach(function (n) { n.el.classList.toggle('actief', n === k); });
    var rel = kanten.filter(function (e) { return e.a === k || e.b === k; }).map(function (e) {
      var ander = e.a === k ? e.b : e.a;
      return '<li><span class="relatie rel-' + e.type + '">' + e.label + '</span> <a href="/begrippen/' + ander.id + '"><span class="stelsel-code">' + ander.stelsel + '</span> ' + esc(ander.term) + '</a>' + (e.toelichting ? '<div class="toelichting">' + esc(e.toelichting) + '</div>' : '') + '</li>';
    }).join('');
    paneel.innerHTML = '<button class="knop-tekst sluit" aria-label="Sluiten">×</button>' +
      '<p class="kruimel">' + k.stelsel + ' · ' + k.taal + '</p><h3 class="serif">' + esc(k.term) + '</h3>' +
      (k.vindplaats ? '<p class="stil klein">' + esc(k.vindplaats) + '</p>' : '') +
      (k.definitie ? '<p>' + esc(k.definitie) + '</p>' : '') +
      (rel ? '<ul class="relatielijst">' + rel + '</ul>' : '<p class="stil">Geen relaties.</p>') +
      '<p><a class="knop klein" href="/begrippen/' + k.id + '">Open begrip</a></p>';
    paneel.hidden = false;
    paneel.querySelector('.sluit').addEventListener('click', function () { paneel.hidden = true; knopen.forEach(function (n) { n.el.classList.remove('actief'); }); });
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  svg.addEventListener('click', function () { paneel.hidden = true; knopen.forEach(function (n) { n.el.classList.remove('actief'); }); });

  // Stelsels filteren
  document.querySelectorAll('input[data-stelsel]').forEach(function (cb) {
    cb.addEventListener('change', function () {
      knopen.forEach(function (k) { if (k.stelsel === cb.dataset.stelsel) k.zichtbaar = cb.checked; });
      wek();
    });
  });

  window.addEventListener('resize', function () {
    W = svg.clientWidth || W; H = svg.clientHeight || H; svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    stelsels.forEach(function (s, i) { anker[s].x = stelsels.length > 1 ? (W * (i + 0.5)) / stelsels.length : W / 2; anker[s].y = H / 2; });
    wek();
  });

  requestAnimationFrame(stap);
})();

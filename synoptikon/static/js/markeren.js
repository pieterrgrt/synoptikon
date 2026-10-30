// Markeren: selecteer tekst in [data-markeerbaar], kies een soort in het kleine menu. Geen afhankelijkheden.
(function () {
  var doel = document.querySelector('[data-markeerbaar]');
  if (!doel) return;
  var d = doel.dataset, menu = null;

  function sluit() { if (menu) { menu.remove(); menu = null; } }

  function context(range) {
    var voor = document.createRange();
    voor.selectNodeContents(doel);
    voor.setEnd(range.startContainer, range.startOffset);
    var begin = voor.toString().length, tekst = doel.textContent, eind = begin + range.toString().length;
    return { voor: tekst.slice(Math.max(0, begin - 40), begin), na: tekst.slice(eind, eind + 40) };
  }

  function bewaar(quote, ctx, soort, notitie, vak) {
    var f = new FormData();
    f.append('quote', quote); f.append('voor', ctx.voor); f.append('na', ctx.na);
    f.append('soort', soort); f.append('notitie', notitie); f.append('vak', vak);
    if (d.bron) f.append('bron_id', d.bron);
    else { f.append('stelsel', d.stelsel); f.append('wet', d.wet || ''); f.append('nummer', d.nummer); }
    return fetch('/markeringen', { method: 'POST', body: f, credentials: 'same-origin' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); window.getSelection().removeAllRanges(); location.reload(); })
      .catch(function () { sluit(); });
  }

  function toon(range) {
    sluit();
    var quote = range.toString().trim(), ctx = context(range), r = range.getBoundingClientRect();
    menu = document.createElement('div');
    menu.className = 'markeer-menu';
    menu.setAttribute('role', 'dialog');
    var notitie = document.createElement('input');
    notitie.type = 'text'; notitie.placeholder = d.lNotitie; notitie.setAttribute('aria-label', d.lNotitie);
    var vak = document.createElement('select');
    vak.setAttribute('aria-label', d.lVak);
    (d.vakken ? d.vakken.split(',') : []).concat(d.vak && d.vakken.split(',').indexOf(d.vak) < 0 ? [d.vak] : []).forEach(function (v) {
      var o = document.createElement('option'); o.textContent = v; if (v === d.vak) o.selected = true; vak.appendChild(o);
    });
    ['kern', 'voorwaarde', 'let_op'].forEach(function (soort) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'knop klein m-' + soort; b.textContent = d['l' + soort.charAt(0).toUpperCase() + soort.slice(1)];
      b.addEventListener('click', function () { bewaar(quote, ctx, soort, notitie.value, vak.value); });
      menu.appendChild(b);
    });
    menu.appendChild(vak); menu.appendChild(notitie);
    // mousedown in het menu mag de selectie niet opheffen
    menu.addEventListener('mousedown', function (e) { if (e.target.tagName === 'BUTTON') e.preventDefault(); });
    document.body.appendChild(menu);
    var top = r.bottom + window.scrollY + 6, links = Math.max(8, Math.min(r.left + window.scrollX, window.innerWidth - menu.offsetWidth - 8));
    menu.style.top = top + 'px'; menu.style.left = links + 'px';
  }

  function bekijk() {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) return;
    var range = sel.getRangeAt(0);
    if (!doel.contains(range.commonAncestorContainer) || range.toString().trim().length < 3) return;
    toon(range);
  }

  doel.addEventListener('mouseup', function () { setTimeout(bekijk, 0); });
  doel.addEventListener('touchend', function () { setTimeout(bekijk, 350); });
  doel.addEventListener('keyup', function (e) { if (e.shiftKey) bekijk(); });
  document.addEventListener('mousedown', function (e) { if (menu && !menu.contains(e.target)) sluit(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') sluit(); });
})();

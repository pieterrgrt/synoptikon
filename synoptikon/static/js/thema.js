// Thema vóór het renderen zetten om flikkeren te voorkomen (extern i.v.m. CSP).
try { var t = localStorage.getItem('thema'); if (t) document.documentElement.dataset.theme = t; } catch (e) {}
// Favicon volgt een handmatig gekozen thema; bij 'auto' doet favicon.svg dat zelf via prefers-color-scheme.
window.zetFavicon = function () {
  var l = document.getElementById('favicon'), t = document.documentElement.dataset.theme;
  if (l) l.href = '/static/favicon' + (t === 'dark' ? '-donker' : t === 'light' ? '-licht' : '') + '.svg?v=3';
};
window.zetFavicon();

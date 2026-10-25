// Thema vóór het renderen zetten om flikkeren te voorkomen (extern i.v.m. CSP).
try { var t = localStorage.getItem('thema'); if (t) document.documentElement.dataset.theme = t; } catch (e) {}

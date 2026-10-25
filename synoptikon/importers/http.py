from __future__ import annotations

import httpx

UA = "Synoptikon/0.1 (persoonlijke rechtsvergelijkingsapp; httpx)"


def client(**kw) -> httpx.Client:
    kw.setdefault("timeout", 60.0)
    kw.setdefault("follow_redirects", True)
    kw.setdefault("headers", {"User-Agent": UA})
    return httpx.Client(**kw)

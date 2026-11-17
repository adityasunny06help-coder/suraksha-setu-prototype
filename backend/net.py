"""HTTP client factory — sandbox/proxy/TLS quirks ek jagah handle hote hain.

Seekh (50-project program, P6): environment ke proxy + MITM CA ko mock tests
chhupa dete hain. Isliye:
- verify = SSL_CERT_FILE env (agar set hai), warna default CA bundle.
- proxy = HTTPS_PROXY/https_proxy env se EXPLICIT pass hota hai aur
  trust_env=False rehta hai (no_proxy parsing ke crashes se bachav).
- Client ban hi na paye to None — caller graceful degrade karega.
"""
import os

import httpx


def make_client(timeout=10.0):
    kwargs = {"timeout": timeout, "follow_redirects": True, "trust_env": False}
    ca = os.environ.get("SSL_CERT_FILE")
    if ca:
        kwargs["verify"] = ca
    proxy = (os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
             or os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy"))
    try:
        if proxy:
            return httpx.Client(proxy=proxy, **kwargs)
        return httpx.Client(**kwargs)
    except Exception:
        try:
            return httpx.Client(timeout=timeout, follow_redirects=True)
        except Exception:
            return None

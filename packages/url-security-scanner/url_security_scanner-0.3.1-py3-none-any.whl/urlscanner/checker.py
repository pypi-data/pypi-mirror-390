from __future__ import annotations
import ipaddress
import socket
from typing import Dict, Tuple, List
import httpx
import urllib.parse as up


HEADERS_TO_CHECK = [
    ("strict-transport-security", "HSTS"),
    ("content-security-policy", "CSP"),
    ("x-frame-options", "XFO"),
    ("x-content-type-options", "XCTO"),
    ("referrer-policy", "REFPOL"),
]


TIMEOUT = httpx.Timeout(10.0, connect=5.0)
UA = {"User-Agent": "ThreatBoard-Header-Audit/0.3"}


PRIVATE_NETS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]




def _is_private_ip(host: str) -> bool:
    try:
        infos = socket.getaddrinfo(host, None)
        for family, _, _, _, sockaddr in infos:
            ip_str = sockaddr[0]
            ip = ipaddress.ip_address(ip_str)
            if any(ip in net for net in PRIVATE_NETS):
                return True
        return False
    except socket.gaierror:
        return False




def _score(headers: httpx.Headers) -> Tuple[int, Dict[str, dict], List[str]]:
    hget = lambda k: headers.get(k)
    results: Dict[str, dict] = {}
    missing: List[str] = []
    score = 0


    # HSTS: +2 if max-age >= 15552000
    hsts = hget("strict-transport-security")
    hsts_ok = False
    if hsts:
        try:
            parts = {p.split("=")[0].strip().lower(): p.split("=", 1)[1] for p in [x.strip() for x in hsts.split(";") if "=" in x]}
            max_age = int(parts.get("max-age", "0"))
            if max_age >= 15552000:
                score += 2
                hsts_ok = True
        except Exception:
            pass
    else:
        missing.append("Strict-Transport-Security")
    results["Strict-Transport-Security"] = {"present": bool(hsts), "value": hsts, "ok": hsts_ok}


    # CSP: +2 if present (no linting in MVP)
    csp = hget("content-security-policy")
    if csp:
        score += 2
    else:
        missing.append("Content-Security-Policy")
    results["Content-Security-Policy"] = {"present": bool(csp), "value": csp, "ok": bool(csp)}


    # XFO: +2 if DENY or SAMEORIGIN
    xfo = hget("x-frame-options")
    xfo_ok = (xfo or "").upper() in {"DENY", "SAMEORIGIN"}
    if xfo_ok:
        score += 2
    else:
        if not xfo:
            missing.append("X-Frame-Options")
    results["X-Frame-Options"] = {"present": bool(xfo), "value": xfo, "ok": xfo_ok}


    # XCTO: +2 if nosniff
    xcto = hget("x-content-type-options")
    xcto_ok = (xcto or "").lower() == "nosniff"
    if xcto_ok:
        score += 2
    else:
        if not xcto:
            missing.append("X-Content-Type-Options")
    results["X-Content-Type-Options"] = {"present": bool(xcto), "value": xcto, "ok": xcto_ok}


    # Referrer-Policy: +2 if present
    refpol = hget("referrer-policy")
    if refpol:
        score += 2
    else:
        missing.append("Referrer-Policy")
    results["Referrer-Policy"] = {"present": bool(refpol), "value": refpol, "ok": bool(refpol)}


    return score, results, missing




def audit_url(url: str) -> dict:
    # Basic SSRF safety: block localhost/private IPs
    parsed = up.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("unsupported scheme")
    if not parsed.netloc:
        raise ValueError("invalid URL")


    host = parsed.hostname or ""
    if host.endswith(".onion") or _is_private_ip(host):
        raise ValueError("disallowed host")


    # Try HEAD, fall back to GET (some sites block HEAD)
    with httpx.Client(headers=UA, timeout=TIMEOUT, follow_redirects=True) as client:
        try:
            resp = client.head(url)
            if resp.status_code in (405, 403) or not resp.headers:
                resp = client.get(url, headers={**UA, "Range": "bytes=0-0"})
        except httpx.HTTPError as e:
            raise RuntimeError(f"fetch failed: {e}")


        score, results, missing = _score(resp.headers)
        effective_url = str(resp.url)


        return {
            "url": url,
            "effective_url": effective_url,
            "scheme": resp.url.scheme,
            "score": score,
            "headers": results,
            "missing": missing,
        }
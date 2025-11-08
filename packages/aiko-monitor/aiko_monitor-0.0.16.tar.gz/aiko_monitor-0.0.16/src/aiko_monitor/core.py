from __future__ import annotations

import base64
import gzip
import hashlib
import hmac
import ipaddress
import json
import re
from typing import Any, Dict, Mapping, Union

# relying on those is fine, in case x-forwarded-for or any other header has been spoofed
PRIORITY_CLIENT_IP_HEADERS = [
    "cf-connecting-ip",
    "x-vercel-forwarded-for",
    "x-sentry-forwarded-for",
    "x-forwarded-for",
    "x-real-ip",
    "x-cluster-client-ip",
    "fastly-client-ip",
]

REDACTION_MASK = "[REDACTED]"
SENSITIVE_KEYS = {
    "password",
    "secret",
    "token",
    "authorization",
    "api_key",
}

Redactable = Union[
    str,
    int,
    float,
    bool,
    None,
    list["Redactable"],
    Mapping[str, "Redactable"],
]


def try_json(buf: bytes | None):
    if not buf:
        return {}
    try:
        import json

        return json.loads(buf.decode("utf-8"))
    except Exception:
        return safe_text(buf)


def safe_text(buf: bytes):
    try:
        return buf.decode("utf-8")
    except Exception:
        return {"base64": buf.hex()}


def body_from_content_type(ct: str, raw: bytes):
    ct = (ct or "").lower()
    if "application/json" in ct:
        try:
            import json

            return json.loads(raw.decode("utf-8"))
        except Exception:
            return raw.decode("utf-8", errors="ignore")
    if ct.startswith("text/") or "html" in ct or "xml" in ct:
        return raw.decode("utf-8", errors="ignore")
    return {"base64": raw.hex()}


def normalize_headers(headers: Dict[str, Any] | None) -> Dict[str, str]:
    if not headers:
        return {}
    out: Dict[str, str] = {}
    for k, v in headers.items():
        if v is None:
            continue
        if isinstance(v, list):
            out[str(k).lower()] = ", ".join(str(x) for x in v)
        else:
            out[str(k).lower()] = str(v)
    return out


def _normalize_ip(value: str) -> str:
    return value.strip().lstrip("[").rstrip("]")


def _valid_ip(s: str) -> bool:
    candidate = _normalize_ip(s)
    try:
        ipaddress.ip_address(candidate)
        return True
    except Exception:
        return False


def _first_from_list(v: str) -> str | None:
    for part in (p.strip().strip('"') for p in v.split(",") if p.strip()):
        if _valid_ip(part):
            return _normalize_ip(part)
    return None


def extract_client_ip(headers: Mapping[str, str], peer_ip: str | None) -> str | None:
    lowered = {k.lower(): v for k, v in headers.items()}
    # 1) vendor/forwarded headers (take first ip if list)
    for name in PRIORITY_CLIENT_IP_HEADERS:
        value = lowered.get(name)
        if value:
            candidate = _first_from_list(value)
            if candidate:
                return candidate

    forwarded = lowered.get("forwarded")
    # 2) RFC 7239 Forwarded: for=... (newer format, seems to be used in newer nginx configs)
    if forwarded:
        match = re.search(r"(?i)\bfor=([^;,\s]+)", forwarded)
        if match:
            candidate = match.group(1).strip('"')
            if _valid_ip(candidate):
                return _normalize_ip(candidate)

    # 3) fallback: socket peer (this is the ip from the framework, if the app is behind proxy/load balancer, this ip will be this ip and not the client's)
    normalized_peer = normalize_peer_ip(peer_ip)
    if normalized_peer:
        return normalized_peer
    return None


def normalize_peer_ip(peer_ip: str | None) -> str | None:
    if not peer_ip:
        return None
    candidate = _normalize_ip(peer_ip)
    if _valid_ip(candidate):
        return candidate
    return None


def redact_any(x: Redactable) -> Redactable:
    if isinstance(x, dict):
        out: Dict[str, Redactable] = {}
        for k, v in x.items():
            if isinstance(k, str) and k.lower() in SENSITIVE_KEYS:
                out[k] = REDACTION_MASK
            else:
                out[k] = redact_any(v)
        return out
    if isinstance(x, list):
        return [redact_any(i) for i in x]
    return x


def redact_event(evt: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "endpoint": evt["endpoint"],
        "method": evt["method"],
        "status_code": evt["status_code"],
        "request_headers": redact_any(normalize_headers(evt["request_headers"])),
        "request_body": redact_any(evt["request_body"]),
        "response_headers": redact_any(normalize_headers(evt["response_headers"])),
        "response_body": redact_any(evt["response_body"]),
        "duration_ms": evt["duration_ms"],
        "url": evt["url"],
    }


def sign(secret_bytes: bytes, data: bytes) -> str:
    return hmac.new(secret_bytes, data, hashlib.sha256).hexdigest()


# only for testing, just making sure sign is good
def verify(secret_bytes: bytes, data: bytes, hex_sig: str) -> bool:
    try:
        expected = hmac.new(secret_bytes, data, hashlib.sha256).digest()
        provided = bytes.fromhex(hex_sig)
        if len(provided) != len(expected):
            return False
        return hmac.compare_digest(expected, provided)
    except Exception:
        return False


def gzip_event(event: Dict[str, Any]) -> bytes:
    payload = json.dumps(event).encode("utf-8")
    return gzip.compress(payload)


def b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def ensure_bytes(parts: list[Any]) -> bytes:
    buf = bytearray()
    for p in parts:
        if isinstance(p, (bytes, bytearray)):
            buf += p
        else:
            buf += str(p).encode("utf-8", errors="replace")
    return bytes(buf)

"""
MediCafe/api_hints.py

Lightweight, XP/Python 3.4.4 compatible helpers to emit concise console hints
for common network/DNS issues and 404 route mismatches. No dependencies; avoid
PHI/PII; intended to be called from exception handlers only.
"""

import sys


def _safe_print(message, console):
    """Print only when console is True; guard against unexpected stdout issues."""
    if not console:
        return
    try:
        # Avoid encoding crashes on legacy consoles
        sys.stdout.write(str(message) + "\n")
        sys.stdout.flush()
    except Exception:
        try:
            print(str(message))
        except Exception:
            pass


def _normalize_text(value):
    try:
        return (value or "").strip().lower()
    except Exception:
        try:
            return str(value).strip().lower()
        except Exception:
            return ""


def _is_likely_dns_or_connectivity_error(error_text):
    text = _normalize_text(error_text)
    # Broad but safe indicators seen from urllib3/requests/socket layers
    patterns = [
        "getaddrinfo failed",                    # DNS resolution failure (Windows errno 11001)
        "name or service not known",             # *nix DNS failure
        "nodename nor servname provided",
        "temporary failure in name resolution",
        "failed to establish a new connection",  # connection-level failure
        "max retries exceeded with url",         # transport retries exhausted
        "connection aborted",
        "connection refused",
        "timed out",
        "certificate verify failed"              # network path ok but TLS chain issue
    ]
    for p in patterns:
        if p in text:
            return True
    return False


def emit_network_hint(endpoint_name, target_url, exception_obj, console=False):
    """
    Emit a concise network/proxy/DNS troubleshooting hint.

    Parameters:
        endpoint_name (str): Logical endpoint (e.g., 'UHCAPI', 'OPTUMAI')
        target_url (str): URL attempted
        exception_obj (Exception): The original exception
        console (bool): If True, prints to console
    """
    try:
        err_text = str(exception_obj)
    except Exception:
        err_text = ""

    # Only emit on probable network/DNS classes; keep messages brief and generic.
    if not _is_likely_dns_or_connectivity_error(err_text):
        return

    try:
        _safe_print("[Connectivity hint] {} call to {} appears to have failed before authentication.".format(endpoint_name, target_url), console)
        _safe_print("This often indicates DNS/proxy/firewall issues rather than an OAuth problem.", console)
        _safe_print("Quick checks (Windows): nslookup host; Test-NetConnection host -Port 443;", console)
        _safe_print("If issues persist: ipconfig /flushdns; netsh winsock reset; netsh int ip reset;", console)
        _safe_print("Also verify proxy: netsh winhttp show proxy (or set HTTPS_PROXY env for this process).", console)
        _safe_print("Note: Do not include PHI/PII in any shared logs.", console)
    except Exception:
        # Best-effort only; never raise from hinting.
        pass


def emit_404_route_hint(method, url, status_code, response_content, console=False):
    """
    Emit a concise route/path troubleshooting hint for provider 404s that say
    "no Route matched with those values".
    """
    try:
        if int(status_code) != 404:
            return
    except Exception:
        return

    try:
        body_text = _normalize_text(response_content)
        if not body_text:
            return
        if ("no route matched" not in body_text) and ("no route" not in body_text):
            return
    except Exception:
        return

    try:
        _safe_print("[Route hint] {} {} returned 404 'no route matched'.".format(method, url), console)
        _safe_print("Verify endpoint path in config, and ensure no double/missing slashes in URL join.", console)
        _safe_print("Providers may deprecate paths; compare with latest swagger/docs.", console)
        _safe_print("Also check unintended environment headers influencing routing (e.g., 'env: sandbox').", console)
    except Exception:
        pass



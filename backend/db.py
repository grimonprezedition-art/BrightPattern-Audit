"""
BrightPattern-Audit — Database layer (via DreamHost PHP proxy)
MySQL lives on DreamHost; VPS cannot access it directly.
All reads/writes go through brightpattern_db.php.
"""

import os
import json
import requests

_PROXY_URL    = os.environ["BP_PROXY_URL"]     # https://xi-app.pro/brightpattern/brightpattern_db.php
_PROXY_SECRET = os.environ["BP_PROXY_SECRET"]  # shared secret header

_HEADERS = {
    "Content-Type": "application/json",
    "X-BP-Secret": _PROXY_SECRET,
}
_TIMEOUT = 10


def insert_batch(records: list[dict], source_ip: str | None = None) -> list[int]:
    rows = []
    for r in records:
        row = {**r, "source_ip": source_ip}
        if isinstance(row.get("matched_signals"), list):
            row["matched_signals"] = json.dumps(row["matched_signals"])
        rows.append(row)

    resp = requests.post(
        f"{_PROXY_URL}?action=insert",
        headers=_HEADERS,
        json=rows,
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json().get("ids", [])


def fetch_stats() -> dict:
    resp = requests.get(
        f"{_PROXY_URL}?action=stats",
        headers=_HEADERS,
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()

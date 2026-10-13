#!/usr/bin/env python3
"""Non-invasive public FiveM endpoint smoke checks. Python 3.11+, stdlib only."""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = json.loads((ROOT / "checks" / "endpoints.json").read_text())
UA = "Livvux-fivem-api-monitor/1.0 (+https://github.com/Livvux/fivem-api)"
BLOCKED = {401, 403, 429, 451}


def validate(name, data):
    if name == "changelog":
        return isinstance(data, dict) and any(k in data for k in ("latest", "recommended", "critical"))
    if name == "counts":
        return isinstance(data, dict)
    if name == "featured":
        return isinstance(data, dict) and isinstance(data.get("servers"), list)
    if name == "single":
        return isinstance(data, dict) and isinstance(data.get("Data"), dict) and bool(data.get("EndPoint"))
    if name == "tweets":
        return isinstance(data, (dict, list))
    if name == "pool":
        return isinstance(data, (dict, list))
    return False


def probe(item, timeout):
    req = urllib.request.Request(item["url"], headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            raw = res.read(1_000_001)
            if len(raw) > 1_000_000:
                return "inconclusive", "response over 1 MB limit"
            if res.status != 200:
                return "fail", f"HTTP {res.status}"
            data = json.loads(raw)
            return ("pass", "JSON schema OK") if validate(item["schema"], data) else ("fail", "JSON schema mismatch")
    except urllib.error.HTTPError as err:
        if err.code in BLOCKED or 500 <= err.code <= 599:
            return "inconclusive", f"HTTP {err.code} (access/rate-limit/server)"
        return "fail", f"HTTP {err.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        return "inconclusive", f"network failure: {type(err).__name__}"
    except (ValueError, UnicodeError):
        return "fail", "invalid JSON"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Validate manifest only")
    parser.add_argument("--timeout", type=int, default=12)
    parser.add_argument("--output", default="endpoint-results.json")
    args = parser.parse_args()
    seen = set()
    for item in CHECKS:
        assert set(item) >= {"id", "url", "schema"}, item
        assert item["id"] not in seen, "duplicate check id"
        assert item["url"].startswith("https://"), "HTTPS required"
        assert item["schema"] in {"changelog", "counts", "featured", "single", "tweets", "pool"}
        seen.add(item["id"])
    if args.offline:
        print(f"Manifest valid: {len(CHECKS)} checks")
        return 0
    results = []
    for item in CHECKS:
        state, detail = probe(item, args.timeout)
        results.append({"id": item["id"], "url": item["url"], "status": state, "detail": detail})
        print(f"{state.upper():12} {item['id']:24} {detail}", flush=True)
    report = {"checked_at": dt.datetime.now(dt.timezone.utc).isoformat(), "results": results}
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    failed = [r for r in results if r["status"] == "fail"]
    print(f"Pass: {sum(r['status']=='pass' for r in results)}; Fail: {len(failed)}; Inconclusive: {sum(r['status']=='inconclusive' for r in results)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

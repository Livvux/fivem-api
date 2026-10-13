# API monitoring

Run `python3 scripts/check_endpoints.py --offline` for manifest validation, or `python3 scripts/check_endpoints.py` for live smoke checks.

The daily GitHub Action checks selected small public JSON endpoints and uploads a timestamped report. A confirmed unexpected HTTP response or JSON contract mismatch fails the run and creates/updates one tracking issue. HTTP 401/403/429/451, 5xx, timeouts and network errors are **inconclusive** (not proof of deprecation); inspect them manually. Checks are intentionally conservative.

## Scope and limits

- This is **not** a complete verification of all documented endpoints.
- The ~20 MB Protobuf server stream is **not downloaded** by the scheduled job (avoid bandwidth and rate limits); its framing/schema and redirect need separate low-frequency manual verification.
- Local FXServer `info.json`, `dynamic.json`, `players.json` and `perf` require a controlled server fixture and are **not** probed on arbitrary public servers.
- Account, session, policy and upvote endpoints require distinct authorization/safety review; they are not tested.
- Responses are capped at 1 MB; do not store player identifiers or credentials.
- Single-server join IDs can expire; if the fixture disappears, replace with a known stable controlled server before treating a 404 as endpoint removal.
- An API responding with matching basic structure is not a guarantee that all field semantics remain unchanged.

Last comprehensive **manual** verification recorded in the source reference: 2026-09-16. Monitoring results are recorded per workflow run, not silently copied into the documentation.

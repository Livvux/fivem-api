---
name: fivem-api
description: Use when checking FiveM/Cfx.re server status, player counts, or server lists; building tools or scripts around FiveM endpoints (info.json, dynamic.json, players.json, server list, icons, artifacts, changelogs); fetching FXServer artifacts or build changelogs; developing FiveM resources or server configs; or when a task might involve deprecated FiveM API endpoints (servers-frontend.fivem.net, lambda.fivem.net, runtime.fivem.net/tweets.json).
---

# FiveM API

Verified endpoint reference for FiveM / Cfx.re. Live-tested 2026-09-16.
Full details (schemas, protobuf definition, response examples): read `references/api-endpoints.md` in this skill's directory.

## Routing: task → endpoint

| Task | Use |
|------|-----|
| Is a server online / player count / hostname | `GET http://{ip:port}/dynamic.json` |
| Full server info (resources, convars, icon) | `GET http://{ip:port}/info.json` |
| Player list of one server | `GET http://{ip:port}/players.json` |
| Server metrics (Prometheus) | `GET http://{ip:port}/perf` |
| One server from the public server list | `GET https://frontend.cfx-services.net/api/servers/single/{hashId}` (JSON; hashId = `cfx.re/join/{hashId}` code) |
| Full server list | `GET https://frontend.cfx-services.net/api/servers/streamRedir/` → **Protobuf**, ~20 MB, not for polling |
| Server icon from the list | `GET https://frontend.cfx-services.net/api/servers/icon/{joinId}/{iconVersion}.png` |
| Featured/spotlight servers | `GET https://gss.cfx-services.net/v1/public/featured-servers/fivem` |
| Latest server artifacts / changelog | `GET https://changelogs-live.fivem.net/api/changelog/versions/{win32\|linux}/server` |
| FiveM/RedM global player counts | `GET https://runtime.fivem.net/counts.json` / `https://static.cfx.re/runtime/counts_rdr3.json` |
| Natives dumps | `https://static.cfx.re/natives/natives.lua` (RedM: `natives_rdr3.lua`) |

## Critical gotchas

- **Dead endpoints — never use** (deprecated community docs list them): `servers-frontend.fivem.net/api/servers/streamRedir` (old host/path → 404), `lambda.fivem.net` (503), `cnl-hb-live.fivem.net`, `sentry.fivem.net`, `runtime.fivem.net/tweets.json`. The server list backend moved to `frontend.cfx-services.net` / `gss.cfx-services.net`.
- Master list (`streamRedir/`) needs the **trailing slash** and returns **Protobuf** (schema in `references/api-endpoints.md`, section 3), not JSON. Single-server endpoint (`single/{hashId}`) is the easy JSON path.
- `single/{ip:port}` does **not** work — only hash IDs.
- Polling the ~20 MB master list causes IP blocks. Poll the target server's `dynamic.json` instead.
- `sv_requestParanoia ≥ 2` on a target server blocks `.json` endpoints for browser-like requests (`"Nope."`).
- `players[].identifiers` in the list API are anonymized; full identifiers only from your own server's `players.json`.

## FiveM development knowledge

For scripting, server setup, convars, events, txAdmin, frameworks (ESX/QBCore/Qbox), performance and security topics, use the fivemdocs.com knowledge base:

- Live site sections: `https://fivemdocs.com/{getting-started,txadmin,frameworks,scripting,ops,security,performance,reference,game-references}/...`
- Source repo (grep/read on demand): `github.com/Livvux/fivemdocs` → `content/**/*.mdx`
- API reference page: `https://fivemdocs.com/reference/api` (same content as this skill's reference file)

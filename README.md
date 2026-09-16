# FiveM / Cfx.re API Documentation

> **Also available as a browsable docs page:** [fivemdocs.com/reference/api](https://fivemdocs.com/reference/api)

> **Last verified:** 2026-09-16 — All endpoints were tested live on the date of creation.
> **Sources:** [docs.fivem.net](https://docs.fivem.net/docs/), [servers.fivem.net](https://servers.fivem.net/) (production frontend bundle analyzed), [github.com/citizenfx/fivem](https://github.com/citizenfx/fivem), [github.com/citizenfx/fivem-docs](https://github.com/citizenfx/fivem-docs), [HAMz-Project/FiveM-Api](https://github.com/HAMz-Project/FiveM-Api) (deprecated)

Legend: ✅ verified · ⚠️ alive, but restricted/needs auth · ❌ dead/unreachable

---

## 1. Live Server HTTP API (every FXServer instance)

Every running FXServer exposes these endpoints on its game port (default `30120`).
Source: `citizenfx/fivem` → `code/components/citizen-server-impl/src/InfoHttpHandler.cpp` (officially referenced in the [Server Commands docs](https://docs.fivem.net/docs/server-manual/server-commands/)).

### 1.1 `GET http://{ip:port}/info.json` ✅

Static server information.

```json
{
  "enforceSteamAuth": false,
  "enhancedHostSupport": true,
  "icon": "iVBORw0KGgo... (base64 PNG, 96x96)",
  "resources": ["resourceA", "resourceB", ...],
  "vars": {
    "sv_maxclients": "2048",
    "sv_projectName": "...",
    "sv_projectDesc": "...",
    "sv_enforceGameBuild": "3258",
    "sv_scriptHookAllowed": "false",
    "gamename": "gta5",
    "locale": "en-EU",
    "onesync_enabled": "true",
    "...": "all sets/sv_* convars"
  },
  "serverVersion": "..."
}
```

### 1.2 `GET http://{ip:port}/dynamic.json` ✅

Dynamic, polling-friendly information (used by the server browser).

```json
{
  "clients": 5,
  "gametype": "Minigames, Races, PvP, and Free Mode",
  "hostname": "^5Mega's Games (EU): ...",
  "iv": "177307322",
  "mapname": "Various",
  "sv_maxclients": "2048"
}
```

| Field | Type | Meaning |
|-------|------|---------|
| `clients` | int | Current player count |
| `sv_maxclients` | string | Max players (`sv_maxclients` convar) |
| `hostname` | string | Hostname with `^` color codes |
| `gametype` / `mapname` | string | From `gametype`/`mapname` convars |
| `iv` | string | Icon version (for icon caching) |

### 1.3 `GET http://{ip:port}/players.json` ✅

Player list.

```json
[
  { "endpoint": "1.2.3.4", "id": 1, "identifiers": ["license:...", "steam:...", "discord:..."], "name": "PlayerName", "ping": 45 },
  { "endpoint": "127.0.0.1", "id": 0, "identifiers": [], "name": "Player", "ping": 0 }
]
```

> ⚠️ The `endpoint` (IP) is hidden with `sv_endpointPrivacy true`.
> ❗ `identifiers` are only fully populated when querying your own server — the server list API strips/anonymizes them.

### 1.4 `GET http://{ip:port}/perf` ✅

Prometheus text-format metrics (tick times, RAM, players, etc.).

```
# HELP tickTime Time spent on server ticks
# TYPE tickTime histogram
tickTime_count{name="svMain"} 78247
...
```

> Auth (optional): `sv_prometheusBasicAuthUser` / `sv_prometheusBasicAuthPassword` in `server.cfg`. Also polled by txAdmin.

### 1.5 Important notes

- **`sv_requestParanoia` ≥ 2** blocks all `.json` endpoints for browser-like requests (response: `"Nope."`).
- The `.json` endpoints are part of the FXServer core — always available, no resource required.
- Ports: TCP `30120` = HTTP/file server, UDP `30120` = game/RCon.

---

## 2. Server List API (backend of servers.fivem.net)

The frontend at `servers.fivem.net` is an SPA; the actual API lives on **`frontend.cfx-services.net`** (extracted from the production bundle).

**Base URL:** `https://frontend.cfx-services.net/api/servers`

### 2.1 All servers (master list) ✅

```
GET https://frontend.cfx-services.net/api/servers/streamRedir/
  → 302 redirect to:
GET https://frontend.cfx-services.net/api/servers/stream/{unixTimestamp}/
  → 200, ~20 MB response
```

- **Format: Protobuf** (no longer JSON!). Layout: repeated `[…4-byte LE length…][master.Server message]`.
- Schema see [section 3](#3-protobuf-schema-master).
- ⚠️ Scale: tens of thousands of servers, ~20 MB download. Not suitable for polling.
- ❌ The old URL `https://servers-frontend.fivem.net/api/servers/streamRedir` (no trailing slash, old host) returns **404**.

### 2.2 Single server ✅

```
GET https://frontend.cfx-services.net/api/servers/single/{hashId}
```

`{hashId}` = short ID from the server list, identical to the **`cfx.re/join/{hashId}`** connect code (e.g. `moyejq`).

Response shape (identical to `info.json`):

```json
{
  "EndPoint": "moyejq",
  "Data": {
    "hostname": "^5Mega's Games (EU): ...",
    "gametype": "...", "mapname": "...",
    "clients": 6, "sv_maxclients": 2048, "svMaxclients": 2048,
    "server": "FXServer-master v1.0.0.35945 linux",
    "enhancedHostSupport": true,
    "iconVersion": -1292580404,
    "vars": { "...": "same as info.json vars" },
    "connectEndPoints": ["79.127.215.11:30120"],
    "players": [ { "name": "...", "identifiers": [...], "ping": 0, "id": 0, "endpoint": "..." } ]
  }
}
```

> `GET …/single/{ip:port}` with the legacy address form returns `404 Not Found` — only hash IDs are accepted.

### 2.3 Server icon ✅ (URL pattern from the frontend bundle)

```
GET https://frontend.cfx-services.net/api/servers/icon/{joinId}/{iconVersion}.png
```

`iconVersion` comes from `Data.iconVersion` (cache-busting int).

### 2.4 Featured / spotlight servers ✅

```
GET https://gss.cfx-services.net/v1/public/featured-servers/fivem
```

```json
{
  "home_page_server": { "type": "collection", "name": "Mega's Games", "hash_ids": ["moyejq","7bb4dpe"] },
  "servers": [
    { "type": "single", "name": "FiveM Test Server", "hash_id": "y4lg95" },
    { "type": "collection", "name": "RSM Freeroam", "hash_ids": ["vjarme","wqxomp"] }
  ]
}
```

Featured server criteria: [docs.fivem.net/docs/server-manual/featured-server-list/](https://docs.fivem.net/docs/server-manual/featured-server-list/) (handpicked, no applications accepted).

### 2.5 Tweets (displayed on the server list) ✅

```
GET https://gss.cfx-services.net/v1/public/tweets
```

### 2.6 Upvote API ⚠️

```
https://servers-frontend.fivem.net/api/upvote/   → 403 (requires Cfx.re session token)
```

Only usable from the game/frontend context with auth. Not a public endpoint.

---

## 3. Protobuf Schema (`master`)

Extracted from the `servers.fivem.net` production bundle (protobuf.js runtime).

```protobuf
syntax = "proto3";
package master;

message Player {
  string name = 1;
  repeated string identifiers = 2;
  string endpoint = 3;
  int32 ping = 4;
  int32 id = 5;
}

message ServerData {
  int32 svMaxclients = 1;
  int32 clients = 2;
  int32 protocol = 3;
  string hostname = 4;
  string gametype = 5;
  string mapname = 6;
  repeated string resources = 8;
  string server = 9;                 // e.g. "FXServer-master v1.0.0.35945 linux"
  repeated Player players = 10;
  int32 iconVersion = 11;
  map<string, string> vars = 12;
  bool enhancedHostSupport = 16;
  int32 upvotePower = 17;
  repeated string connectEndPoints = 18;
  int32 burstPower = 19;
}

message Server {
  string EndPoint = 1;               // hash ID or endpoint
  ServerData Data = 2;
  int32 id = 3;                      // internal list field (joinId)
}
```

**Stream container format:** `u32 (LE)` message length, followed by exactly that many bytes of `Server` message — repeated until end of stream.

---

## 4. Cfx.re Runtime & Infrastructure Endpoints

All GET, public, no auth.

### 4.1 Player counters

| Endpoint | Status | Content |
|----------|--------|---------|
| `https://runtime.fivem.net/counts.json` | ✅ 200 | FiveM player/server counters |
| `https://static.cfx.re/runtime/counts.json` | ✅ 200 | same (static CDN) |
| `https://static.cfx.re/runtime/counts_rdr3.json` | ✅ 200 | RedM counters |

### 4.2 Pinned / promoted / blacklist

| Endpoint | Status | Content |
|----------|--------|---------|
| `https://runtime.fivem.net/pins.json` | ✅ 200 | Pinned/top servers |
| `https://runtime.fivem.net/promotions_targeting.json` | ✅ 200 | Promotion targeting |
| `https://runtime.fivem.net/nui-blacklist.json` | ✅ 200 | NUI domain blacklist |

### 4.3 Pool size limits (for `increase_pool_size`)

| Endpoint | Status |
|----------|--------|
| `https://content.cfx.re/mirrors/client/pool-size-limits/fivem.json` | ✅ 200 |
| `https://content.cfx.re/mirrors/client/pool-size-limits/redm.json` | ✅ 200 |

### 4.4 Natives dumps

| Endpoint | Status |
|----------|--------|
| `https://static.cfx.re/natives/natives.lua` | ✅ 200 |
| `https://static.cfx.re/natives/natives_rdr3.lua` | ✅ 200 |

### 4.5 Server artifacts & changelog ✅

```
GET https://changelogs-live.fivem.net/api/changelog/versions/{win32|linux}/server
```

```json
{
  "critical": "7290",
  "recommended": "35245",
  "optional": "7290",
  "latest": "35945",
  "critical_txadmin": "7.0.0",
  "critical_download": "https://runtime.fivem.net/artifacts/fivem/build_server_windows/master/7290-<hash>/server.zip",
  "recommended_download": "https://runtime.fivem.net/artifacts/fivem/build_server_windows/master/35245-<hash>/server.zip",
  "latest_download": "..."
}
```

- Single build: `GET …/api/changelog/versions/win32/server/{buildNumber}` (build number, not version string).
- Client artifacts analog: `https://runtime.fivem.net/artifacts/fivem/` (directory listing).

### 4.6 Policy / user info

| Endpoint | Status | Content |
|----------|--------|---------|
| `https://policy-live.fivem.net/api/getUserInfo/{id}` | ✅ 200 | Policy status of a user |

---

## 5. Forum / Account API (forum.cfx.re = Discourse)

Base: `https://forum.cfx.re` — standard Discourse API endpoints. Without login cookies, session endpoints return 404/403.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/session/current.json` | GET | Current session (only with cookie/auth) |
| `/session/csrf.json` | GET | CSRF token |
| `/u/{username}.json` | GET | Public profile |
| `/u/check_username.json?username={username}` | GET | Username availability |
| `/u/check_email.json?email={email}` | GET | Email availability |
| `/u/action/send_activation_email` | POST | Activation email (headers: `Cfx-Entitlement-Ticket`, `x-csrf-token`, `discourse-present: true`, `x-requested-with: XMLHttpRequest`) |

---

## 6. Server Management (not an HTTP REST API, but relevant)

### 6.1 RCon

- Activation: `rcon_password <pw>` in `server.cfg` — **FXServer RCon runs over UDP** on the game port.
- Custom RCon commands: `RegisterCommand` (server-side) or the legacy `rconCommand` event.

### 6.2 Most important server commands (via RCon/console)

`start`/`stop`/`ensure`/`restart [resource]`, `refresh`, `exec [file]`, `quit [reason]`, `status`, `clientkick [id] [reason]`, `say [msg]`, `svgui`
→ Full list: [docs.fivem.net/docs/server-manual/server-commands/](https://docs.fivem.net/docs/server-manual/server-commands/)

### 6.3 txAdmin

- Local web API at `http://localhost:40120/` (token in `txData/txAdmin/cache/*.key`).
- Remote REST API: `https://txadmin.cfx.re` (only with the server's txAdmin token).

---

## 7. Status of the old HAMz-Project/FiveM-Api list (tested 2026-09-16)

| Endpoint | Status | Replacement |
|----------|--------|-------------|
| `http://{ip:port}/info.json` | ✅ | — (alive) |
| `http://{ip:port}/dynamic.json` | ✅ | — (alive) |
| `http://{ip:port}/players.json` | ✅ | — (alive) |
| `servers-frontend.fivem.net/api/servers/single/{address}` | ⚠️ → ✅ | New host: `frontend.cfx-services.net/api/servers/single/{hashId}` |
| `servers-frontend.fivem.net/api/servers/streamRedir` | ❌ 404 | `frontend.cfx-services.net/api/servers/streamRedir/` (trailing slash!, now Protobuf) |
| `servers-frontend.fivem.net/api/servers/top/{language}` | ❌ | `gss.cfx-services.net/v1/public/featured-servers/fivem` |
| `servers-frontend.fivem.net/api/upvote/` | ⚠️ 403 | Only with Cfx session auth |
| `lambda.fivem.net/api/ticket/playtimes/...` | ❌ 503 | no public replacement |
| `lambda.fivem.net` / `cnl-hb-live.fivem.net` | ❌ | dead/unreachable |
| `sentry.fivem.net/auth/login` | ❌ | dead |
| `runtime.fivem.net/promotions_targeting.json` | ✅ | — |
| `runtime.fivem.net/pins.json` | ✅ | — |
| `changelogs-live.fivem.net/api/changelog/versions/{buildversion}` | ⚠️ | Format now: `/api/changelog/versions/{win32\|linux}/server[/{build}]` |
| `changelogs-live.fivem.net/api/changelog/versions/win32/server` | ✅ | — |
| `runtime.fivem.net/nui-blacklist.json` | ✅ | — |
| `runtime.fivem.net/counts.json` | ✅ | — |
| `static.cfx.re/runtime/counts.json` | ✅ | — |
| `static.cfx.re/runtime/counts_rdr3.json` | ✅ | — |
| `runtime.fivem.net/tweets.json` | ❌ | `gss.cfx-services.net/v1/public/tweets` |
| `runtime.fivem.net/loadscreen/...` | — | no longer relevant |
| `content.cfx.re/mirrors/client/pool-size-limits/fivem.json` | ✅ | — |
| `content.cfx.re/mirrors/client/pool-size-limits/redm.json` | ✅ | — |
| `static.cfx.re/natives/natives.lua` | ✅ | — |
| `static.cfx.re/natives/natives_rdr3.lua` | ✅ | — |
| `policy-live.fivem.net/api/getUserInfo/{id}` | ✅ | — |
| `forum.cfx.re/*` (Discourse) | ⚠️ | alive; session endpoints need auth |

---

## 8. Client / In-Game "APIs" (distinction)

Not HTTP endpoints, but scripting surfaces — reference only:

- **Natives:** ~[docs.fivem.net/natives/](https://docs.fivem.net/natives/) (dump: `static.cfx.re/natives/natives.lua`)
- **Events:** `playerConnecting`, `playerDropped`, `rconCommand`, … → [events reference](https://docs.fivem.net/docs/scripting-reference/events/list/)
- **Statebags, OneSync, routing buckets:** [docs.fivem.net/docs/scripting-reference/](https://docs.fivem.net/docs/scripting-reference/)

---

## 9. Usage Notes

1. **Rate limits:** Cfx.re does not publish documented public limits, but aggressive polling (especially of the 20 MB stream endpoint) leads to IP blocks. For live status: always poll `info.json`/`dynamic.json` directly on the target server, never the master list.
2. **Protobuf decoding:** The master list requires custom decoding (schema in section 3). The convenient path for single servers: `single/{hashId}` (JSON).
3. **Player data in the master list:** `players[].identifiers` are anonymized/empty there — full identifiers only via your own server (`players.json` on-site).
4. **`cfx.re/join/{hashId}`** resolves to the server (200 ✅) — usable for connect buttons in your own tools.
5. **Official support** exists for none of these endpoints — they are unofficial, except the `.json`/`/perf` endpoints of your own server and those referenced in the docs.

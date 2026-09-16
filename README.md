# FiveM / Cfx.re API-Dokumentation

> **Stand:** 16.09.2026 — Alle Endpunkte wurden am Erstellungsdatum live getestet.
> **Quellen:** [docs.fivem.net](https://docs.fivem.net/docs/), [servers.fivem.net](https://servers.fivem.net/) (Frontend-Bundle analysiert), [github.com/citizenfx/fivem](https://github.com/citizenfx/fivem), [github.com/citizenfx/fivem-docs](https://github.com/citizenfx/fivem-docs), [HAMz-Project/FiveM-Api](https://github.com/HAMz-Project/FiveM-Api) (deprecated)

Legende: ✅ verifiziert · ⚠️ alive, aber eingeschränkt/authpflichtig · ❌ tot/unerreichbar

---

## 1. Live-Server HTTP-API (jeder FXServer-Server)

Jeder laufende FXServer exponiert diese Endpunkte auf seinem Game-Port (Standard `30120`).
Quelle: `citizenfx/fivem` → `code/components/citizen-server-impl/src/InfoHttpHandler.cpp` (offiziell in den [Server Commands Docs](https://docs.fivem.net/docs/server-manual/server-commands/) referenziert).

### 1.1 `GET http://{ip:port}/info.json` ✅

Statische Server-Informationen.

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
    "...": "alle sets/sv_* Convars"
  },
  "serverVersion": "..."
}
```

### 1.2 `GET http://{ip:port}/dynamic.json` ✅

Dynamische, polling-freundliche Informationen (vom Server-Browser benutzt).

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

| Feld | Typ | Bedeutung |
|------|-----|-----------|
| `clients` | int | Aktuelle Spielerzahl |
| `sv_maxclients` | string | Max. Spieler (`sv_maxclients` Convar) |
| `hostname` | string | Hostname mit `^`-Farbcodes |
| `gametype` / `mapname` | string | Aus `gametype`/`mapname` Convars |
| `iv` | string | Icon-Version (für Icon-Caching) |

### 1.3 `GET http://{ip:port}/players.json` ✅

Spielerliste.

```json
[
  { "endpoint": "1.2.3.4", "id": 1, "identifiers": ["license:...", "steam:...", "discord:..."], "name": "Spielername", "ping": 45 },
  { "endpoint": "127.0.0.1", "id": 0, "identifiers": [], "name": "Player", "ping": 0 }
]
```

> ⚠️ `endpoint` (IP) wird mit `sv_endpointPrivacy true` versteckt.
> ❗ `identifiers` sind nur bei eigener Server-Abfrage vollständiger — die Serverlisten-API entfernt/anonymisiert sie.

### 1.4 `GET http://{ip:port}/perf` ✅

Prometheus-Textformat-Metriken (Tick-Zeiten, RAM, Spieler etc.).

```
# HELP tickTime Time spent on server ticks
# TYPE tickTime histogram
tickTime_count{name="svMain"} 78247
...
```

> Auth (optional): `sv_prometheusBasicAuthUser` / `sv_prometheusBasicAuthPassword` in `server.cfg`. Wird auch von txAdmin gepollt.

### 1.5 Wichtige Hinweise

- **`sv_requestParanoia` ≥ 2** blockt alle `.json`-Endpunkte für Browser-artige Requests (Antwort: `"Nope."`).
- `.json`-Endpunkte sind Teil des FXServer-Kerns — immer verfügbar, kein Resource nötig.
- Ports: TCP `30120` = HTTP/File-Server, UDP `30120` = Game/RCon.

---

## 2. Server-Listen-API (Backend von servers.fivem.net)

Das Frontend auf `servers.fivem.net` ist eine SPA; die tatsächliche API liegt auf **`frontend.cfx-services.net`** (aus dem Produktions-Bundle extrahiert).

**Basis:** `https://frontend.cfx-services.net/api/servers`

### 2.1 Alle Server (Master-Liste) ✅

```
GET https://frontend.cfx-services.net/api/servers/streamRedir/
  → 302 Redirect auf:
GET https://frontend.cfx-services.net/api/servers/stream/{unixTimestamp}/
  → 200, ~20 MB Antwort
```

- **Format: Protobuf** (kein JSON mehr!). Aufbau: wiederholt `[…4-Byte-LE-Länge…][master.Server-Message]`.
- Schema siehe [Abschnitt 3](#3-protobuf-schema-master).
- ⚠️ Größenordnung: mehrere zehntausend Server, Download ~20 MB. Nicht für Polling geeignet.
- ❌ Die alte URL `https://servers-frontend.fivem.net/api/servers/streamRedir` (ohne Trailing Slash, alter Host) liefert **404**.

### 2.2 Einzelner Server ✅

```
GET https://frontend.cfx-services.net/api/servers/single/{hashId}
```

`{hashId}` = Short-ID der Serverliste, identisch mit dem **`cfx.re/join/{hashId}`**-Connect-Code (z. B. `moyejq`).

Antwort-Shape (identisch zu `info.json`):

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
    "vars": { "...": "wie info.json vars" },
    "connectEndPoints": ["79.127.215.11:30120"],
    "players": [ { "name": "...", "identifiers": [...], "ping": 0, "id": 0, "endpoint": "..." } ]
  }
}
```

> `GET …/single/{ip:port}` mit alter Adress-Form liefert `404 Not Found` — nur Hash-IDs werden akzeptiert.

### 2.3 Server-Icon ✅ (URL-Pattern aus dem Frontend-Bundle)

```
GET https://frontend.cfx-services.net/api/servers/icon/{joinId}/{iconVersion}.png
```

`iconVersion` kommt aus `Data.iconVersion` (Cache-Busting-Int).

### 2.4 Featured / Spotlight-Server ✅

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

Featured-Server-Criteria: [docs.fivem.net/docs/server-manual/featured-server-list/](https://docs.fivem.net/docs/server-manual/featured-server-list/) (Handpicked, keine Bewerbungen möglich).

### 2.5 Tweets (Auf der Serverliste angezeigt) ✅

```
GET https://gss.cfx-services.net/v1/public/tweets
```

### 2.6 Upvote-API ⚠️

```
https://servers-frontend.fivem.net/api/upvote/   → 403 (erfordert Cfx.re-Session-Token)
```

Nur aus dem Spiel-/Frontend-Kontext mit Auth nutzbar. Kein öffentlicher Endpunkt.

---

## 3. Protobuf-Schema (`master`)

Extrahiert aus dem `servers.fivem.net`-Produktions-Bundle (protobuf.js Runtime).

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
  string server = 9;                 // z.B. "FXServer-master v1.0.0.35945 linux"
  repeated Player players = 10;
  int32 iconVersion = 11;
  map<string, string> vars = 12;
  bool enhancedHostSupport = 16;
  int32 upvotePower = 17;
  repeated string connectEndPoints = 18;
  int32 burstPower = 19;
}

message Server {
  string EndPoint = 1;               // Hash-ID bzw. Endpoint
  ServerData Data = 2;
  int32 id = 3;                      // internes Listen-Feld (joinId)
}
```

**Stream-Container-Format:** `u32 (LE)` Nachrichtenlänge, gefolgt von genau so vielen Bytes `Server`-Message — wiederholt bis Stream-Ende.

---

## 4. Cfx.re Runtime- und Infrastruktur-Endpunkte

Alle GET, öffentlich, ohne Auth.

### 4.1 Spielerzähler

| Endpunkt | Status | Inhalt |
|----------|--------|--------|
| `https://runtime.fivem.net/counts.json` | ✅ 200 | FünfM-Spieler-/Serverzähler |
| `https://static.cfx.re/runtime/counts.json` | ✅ 200 | dto. (statisches CDN) |
| `https://static.cfx.re/runtime/counts_rdr3.json` | ✅ 200 | RedM-Zähler |

### 4.2 Pinned / Promoted / Blacklist

| Endpunkt | Status | Inhalt |
|----------|--------|--------|
| `https://runtime.fivem.net/pins.json` | ✅ 200 | Gepinnte/Top-Server |
| `https://runtime.fivem.net/promotions_targeting.json` | ✅ 200 | Promotion-Targeting |
| `https://runtime.fivem.net/nui-blacklist.json` | ✅ 200 | NUI-Domain-Blacklist |

### 4.3 Pool-Size-Limits (für `increase_pool_size`)

| Endpunkt | Status |
|----------|--------|
| `https://content.cfx.re/mirrors/client/pool-size-limits/fivem.json` | ✅ 200 |
| `https://content.cfx.re/mirrors/client/pool-size-limits/redm.json` | ✅ 200 |

### 4.4 Natives-Dump

| Endpunkt | Status |
|----------|--------|
| `https://static.cfx.re/natives/natives.lua` | ✅ 200 |
| `https://static.cfx.re/natives/natives_rdr3.lua` | ✅ 200 |

### 4.5 Server-Artifacts & Changelog ✅

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

- Einzeln: `GET …/api/changelog/versions/win32/server/{buildNumber}` (Build-Nummer, nicht Versions-String).
- Client-Artifacts analog: `https://runtime.fivem.net/artifacts/fivem/` (Verzeichnis-Listing).

### 4.6 Policy / User-Info

| Endpunkt | Status | Inhalt |
|----------|--------|--------|
| `https://policy-live.fivem.net/api/getUserInfo/{id}` | ✅ 200 | Policy-Status eines Users |

---

## 5. Forum-/Account-API (forum.cfx.re = Discourse)

Basis: `https://forum.cfx.re` — Standard-Discourse-API-Endpunkte. Ohne Login-Cookies geben session-Endpunkte 404/403.

| Endpunkt | Methode | Zweck |
|----------|---------|-------|
| `/session/current.json` | GET | Aktuelle Session (nur mit Cookie/Auth) |
| `/session/csrf.json` | GET | CSRF-Token |
| `/u/{username}.json` | GET | Öffentliches Profil |
| `/u/check_username.json?username={username}` | GET | Username-Verfügbarkeit |
| `/u/check_email.json?email={email}` | GET | E-Mail-Verfügbarkeit |
| `/u/action/send_activation_email` | POST | Aktivierungsmail (Header: `Cfx-Entitlement-Ticket`, `x-csrf-token`, `discourse-present: true`, `x-requested-with: XMLHttpRequest`) |

---

## 6. Server-Verwaltung (keine HTTP-REST-API, aber relevant)

### 6.1 RCon

- Aktivierung: `rcon_password <pw>` in `server.cfg` — **FXServer-RCon läuft über UDP** auf dem Game-Port.
- Custom RCon-Commands: `RegisterCommand` (server) oder Legacy-Event `rconCommand`.

### 6.2 Wichtigste Server-Commands (via RCon/Console)

`start`/`stop`/`ensure`/`restart [resource]`, `refresh`, `exec [file]`, `quit [reason]`, `status`, `clientkick [id] [reason]`, `say [msg]`, `svgui`
→ Vollständig: [docs.fivem.net/docs/server-manual/server-commands/](https://docs.fivem.net/docs/server-manual/server-commands/)

### 6.3 txAdmin

- Lokale Web-API unter `http://localhost:40120/` (Token in `txData/txAdmin/cache/*.key`).
- Fremd-REST-API: `https://txadmin.cfx.re` (nur mit txAdmin-Token des Servers).

---

## 7. Status der alten HAMz-Project/FiveM-Api-Liste (getestet 16.09.2026)

| Endpunkt | Status | Ersatz |
|----------|--------|--------|
| `http://{ip:port}/info.json` | ✅ | — (lebt) |
| `http://{ip:port}/dynamic.json` | ✅ | — (lebt) |
| `http://{ip:port}/players.json` | ✅ | — (lebt) |
| `servers-frontend.fivem.net/api/servers/single/{address}` | ⚠️ → ✅ | Neuer Host: `frontend.cfx-services.net/api/servers/single/{hashId}` |
| `servers-frontend.fivem.net/api/servers/streamRedir` | ❌ 404 | `frontend.cfx-services.net/api/servers/streamRedir/` (Trailing Slash!, jetzt Protobuf) |
| `servers-frontend.fivem.net/api/servers/top/{language}` | ❌ | `gss.cfx-services.net/v1/public/featured-servers/fivem` |
| `servers-frontend.fivem.net/api/upvote/` | ⚠️ 403 | Nur mit Cfx-Session-Auth |
| `lambda.fivem.net/api/ticket/playtimes/...` | ❌ 503 | kein öffentlicher Ersatz |
| `lambda.fivem.net` / `cnl-hb-live.fivem.net` | ❌ | tot/unerreichbar |
| `sentry.fivem.net/auth/login` | ❌ | tot |
| `runtime.fivem.net/promotions_targeting.json` | ✅ | — |
| `runtime.fivem.net/pins.json` | ✅ | — |
| `changelogs-live.fivem.net/api/changelog/versions/{buildversion}` | ⚠️ | Format jetzt: `/api/changelog/versions/{win32\|linux}/server[/{build}]` |
| `changelogs-live.fivem.net/api/changelog/versions/win32/server` | ✅ | — |
| `runtime.fivem.net/nui-blacklist.json` | ✅ | — |
| `runtime.fivem.net/counts.json` | ✅ | — |
| `static.cfx.re/runtime/counts.json` | ✅ | — |
| `static.cfx.re/runtime/counts_rdr3.json` | ✅ | — |
| `runtime.fivem.net/tweets.json` | ❌ | `gss.cfx-services.net/v1/public/tweets` |
| `runtime.fivem.net/loadscreen/...` | — | nicht mehr relevant |
| `content.cfx.re/mirrors/client/pool-size-limits/fivem.json` | ✅ | — |
| `content.cfx.re/mirrors/client/pool-size-limits/redm.json` | ✅ | — |
| `static.cfx.re/natives/natives.lua` | ✅ | — |
| `static.cfx.re/natives/natives_rdr3.lua` | ✅ | — |
| `policy-live.fivem.net/api/getUserInfo/{id}` | ✅ | — |
| `forum.cfx.re/*` (Discourse) | ⚠️ | lebt; Session-Endpunkte brauchen Auth |

---

## 8. Client-/Ingame-"APIs" (Abgrenzung)

Keine HTTP-Endpunkte, sondern Scripting-Oberflächen — hier nur der Verweis:

- **Natives:** ~[docs.fivem.net/natives/](https://docs.fivem.net/natives/) (Dump: `static.cfx.re/natives/natives.lua`)
- **Events:** `playerConnecting`, `playerDropped`, `rconCommand`, … → [Events-Referenz](https://docs.fivem.net/docs/scripting-reference/events/list/)
- **Statebags, OneSync, Routing-Buckets:** [docs.fivem.net/docs/scripting-reference/](https://docs.fivem.net/docs/scripting-reference/)

---

## 9. Nutzungshinweise

1. **Rate Limits:** Cfx.re betreibt keine dokumentierten öffentlichen Limits, aber aggressives Polling (besonders des 20-MB-Stream-Endpunkts) führt zu IP-Blocks. Für Live-Status: immer direkt `info.json`/`dynamic.json` am Zielserver pollen, nie die Master-Liste.
2. **Protobuf-Dekodierung:** Für die Master-Liste eigenes Dekoding nötig (Schema in Abschnitt 3). Bequemer Weg für Einzelserver: `single/{hashId}` (JSON).
3. **Player-Daten in der Master-Liste:** `players[].identifiers` sind dort anonymisiert/leer — vollständige Identifiers nur via eigenem Server (`players.json` vor Ort).
4. **`cfx.re/join/{hashId}`** löst auf den Server auf (200 ✅) — für Connect-Buttons in eigenen Tools nutzbar.
5. **Offizieller Support** existiert für keine dieser Endpunkte — sie sind inoffiziell, außer die `.json`/`/perf`-Endpunkte des eigenen Servers und die in den Docs referenzierten.

# 03 — Product specification

*The contract we hold ourselves to. Where this document and the original disagree, the disagreement is listed in §14 with a reason.*

## 1. The instrument contract

Ten rules. Every page, provider and test is downstream of these.

1. **A number is a measurement or it is nothing.** `0` is only ever a measured zero. The states are `ok`, `unavailable`, `unsupported`, `denied`, `stale`, `error` — never a silent fallback.
2. **Every reading carries provenance.** Metric id, value, unit, state, provider id, native source (a path, a counter name, an API symbol), sample timestamp, sample window, and a human sentence explaining a non-`ok` state.
3. **A gap is data.** History is a time series of samples and voids. Nothing is interpolated across a gap, and no graph draws a line through one.
4. **Identity beats identifiers.** A process is `(pid, start_time, boot_id)`; an interface is `(name, index)`; a disk is `(device, serial, mount)`. Actions revalidate identity immediately before acting and abort loudly if it changed.
5. **Isolation over heroics.** One provider that hangs degrades one tile and is named in the status bar. Nothing blocks the sampling loop.
6. **Least privilege, declared.** No elevation at install, none at launch. Privileged readings are `denied` with the exact grant that would fix it, and the instructions are on a documentation page we ship.
7. **Open by default, local by default.** No telemetry, no account, no licence server, no automatic network request. The daemon listens on localhost. Remote access is opt-in and read-only until explicitly paired as writable.
8. **The instrument must not flinch.** Sampling is scheduled with a monotonic clock, survives sleep, and reports its own cost.
9. **Everything on screen is exportable.** Any table, graph series and recording is available as JSON/CSV from the UI, the CLI and the API.
10. **The interface is not the product.** Console, CLI and remote view read the same core model; none of them is privileged.

## 2. Surfaces

| Surface | Shape | Why it exists |
| --- | --- | --- |
| `vernierd` | Local daemon, single binary | One sampling core, many readers; works headless |
| **Console** | React SPA served by the daemon, opened on `localhost:7420` | The instrument; later wrapped by Tauri for a desktop app |
| `vernier` CLI | JSON-first one-shot and watch modes | Scripts, CI, cron, alerting |
| **Recorder** | Always-on ring buffer + explicit recordings | "What just happened?" without a paid tier |
| **Remote** | Same console over LAN/tailnet with pairing | Fleet and headless boxes |
| **Provider SDK** | JSON-RPC over stdio | Vendor sensors, containers, NAS, anything |
| **Site** | Docs + downloads + checksums | Trust surface for a systems tool |

## 3. Information architecture

Sidebar groups, top to bottom. All destinations are free.

| Group | Destination | Was Pro in TMOG |
| --- | --- | :--: |
| **Overview** | Summary | no |
| | Performance | no |
| | Processes | no |
| **Machine** | System Info | no |
| | Startup apps | no |
| | Users | no |
| | Services | no |
| **Insight** | Power & Frequency | **yes** |
| | Connections | **yes** |
| | Installed Apps | **yes** |
| | Disk Space | **yes** |
| | Benchmarks | **yes** |
| | **Recorder** | **yes (Flight Recorder)** |
| **Beyond** | Fleet *(only when peers are paired)* | — |
| | Advisor *(attribution engine)* | prototype |
| **Footer** | Settings · About · Provider health | — |

Two additions that are ours alone: **Provider health** (every provider, its last sample, error rate, average latency) and **Fleet**.

## 4. Global interface contract

### 4.1 Frame

- Left rail: destination list with section headers, 8 px rhythm, active item marked by a phosphor bar, not a filled block.
- Header: destination name, live status chip (`LIVE · 1 Hz` / `PAUSED` / `DEGRADED 2`), and a command-palette button (`Ctrl/⌘ K`).
- Footer status bar: **provider health dot**, generation counter (`gen 6 021`), process count, load average, uptime, and the gap count in the last minute (`gaps 0`). The gap counter is a first-class citizen: it is how the user knows the instrument is telling the truth.
- Single dark chrome by default; light theme available; no gradients for their own sake.

### 4.2 Meters (VFD)

A meter is a horizontal or vertical column of discrete segments (`n` configurable 4–48 by size). Rendering rules:

- **Lit count** = `round(value / scale × n)`, with the last lit segment optionally bloomed.
- **Scale** is explicit and visible (e.g. `0–100 %`, `0–max clock Hz`, `0–peak rate`). A meter never rescales silently; a rescaled axis is marked `auto`.
- **Animation** eases *toward the newest sample* over ≤120 ms and never invents intermediate values in text. The numeric readout is always the sample.
- **Stale** (>3 sample intervals old) dims the meter and shows `stale 4.2 s`; **void** (no sample) shows the unlit track with a hairline hatch and the state word.
- Colour never carries meaning alone: every channel also has a label and, where relevant, a pattern (P-core solid, E-core hatched).

### 4.3 Graphs

- Multi-series, dual axis allowed (e.g. CPU % left, temperature right), each series with a legend chip that toggles visibility and shows the latest value and its state.
- **Void handling:** series are stored as `(t, value | null)`; a null breaks the path. Consecutive nulls render as a hatched band with the cause (`sleep 62 s`, `provider error`, `no sample`).
- Time base is the daemon's monotonic clock mapped to wall time; **suspend is detected** by comparing `CLOCK_MONOTONIC` with `CLOCK_BOOTTIME` and produces a labelled gap, not a jump.
- Hover shows a crosshair with the sample's timestamp and every series' reading, plus provenance on click.
- Auto-scale with hysteresis: the axis grows immediately and shrinks only after 10 s below 60 % of range, to stop visual breathing.

### 4.4 Tables

Virtualised, keyboard-navigable, sortable on any column, resizable and hideable columns, per-destination persisted layout, right-click verbs, and `Ctrl/⌘ C` that copies the selection as TSV. Filtering is a first-class affordance: a filter that hides the selected row shows an inline "hidden by filter — clear" link (the original added this in 1.1 [A]; we build it in from the start).

### 4.5 States

Every panel implements five states with real copy, not spinners: `loading` (first sample pending, with the provider named), `ok`, `degraded` (some series unavailable, with the reason), `empty` (measured, nothing there), `error` (provider failed, with the last good sample time). No layout shift between states.

## 5. Page specifications

Each page lists its purpose, its zones, its data, and the acceptance test that must pass before it is "done".

### 5.1 Summary

**Purpose:** answer "why is this machine slow right now?" in under five seconds.

**Zones**

1. **Gauge cluster** — CPU busy %, CPU clock, CPU package temperature, GPU busy %. Each gauge is a vertical VFD with value, unit and scale below.
2. **CPU overview** — dual-axis graph: left = busy %, kernel %, right = temperature; legend with live values; footer names the topology ("12 logical · 6 P + 4 E") and the governor/driver.
3. **Top processes** — top 8 by CPU with PID, name, CPU %, memory; a one-click jump to Processes with that row selected and filter cleared.
4. **Memory utilisation** — used/total, available, cached, swap, pressure; a graph with a fill band for pressure.
5. **Load average / tasks** — 1/5/15 min, runnable/total, thread count.
6. **Mini panels** — energy (W and limit), thermals (hotspot + sensor name), disk (busy % and R/W), network (Rx/Tx with units).
7. **Status line** — provider health, generation, gaps.

**Acceptance:** with a synthetic load generator (N busy loops), the top process accounts for ≥ 80 % of the measured total within 2 s, and the cluster never displays a value with state ≠ `ok` without also showing the state word.

### 5.2 Performance

**Purpose:** the per-device deep view.

- Device selector: CPU, GPU (each adapter), Memory, Disk (each device or the combined path), Network (each interface), Energy.
- **CPU:** overall / per logical processor / NUMA toggle; per-core frequency, temperature, P/E class; click a core to pin the graph to it.
- **GPU:** utilisation, VRAM used/total, clocks (graphics/memory), power, temperature, encode/decode engines.
- **Disk:** busy %, throughput, IOPS, queue depth, latency, per-device; a combined "storage path" aggregate that is clearly labelled as a sum.
- **Network:** Rx/Tx rates, packet/error counters, link speed, MTU, addresses; "adaptive scale" with the peak marked.
- **Energy:** instantaneous watts, a history, power state, and the processes responsible (see §9).

**Acceptance:** every device list is derived from enumeration at runtime; unplugging a USB disk removes it without a reload and leaves a gap in history.

### 5.3 Processes

**Purpose:** the table that users live in.

- **Columns:** PID, name, user, CPU %, memory (RSS), private/virtual, disk R+W, network R+W (from the socket join where permission allows, else `unavailable`), threads, handles/FDs, start time, status, parent PID, command line, priority, energy impact.
- **Tree and flat modes** with expand/collapse all; a "follow" toggle that keeps the selection visible.
- **Filter** by name/cmdline/PID with substring and regex modes; scoped-to-subtree filter.
- **Detail pane:** identity (pid, start time, boot id, exe path, cwd, user, session, parent), resources over time (sparklines), open files and sockets (permission-gated), threads, environment (redacted by default), and a provenance card for every reading.
- **Verbs:** end task (SIGTERM / `TerminateProcess` / `SIGTERM` on macOS — note macOS has no polite equivalent, so the UI says what it will do), force kill, suspend/resume, priority ladder, start a new task, open file location, go to details, copy.
- **Safety:** destructive verbs are confirmed with the process identity in the dialog (`name (pid 1234, started 09:41:02)`); a process that changed identity since selection aborts with an explanation; protected processes are marked and disabled rather than failing at click time.

**Acceptance:** the PID-reuse test — a tight fork loop with selection held — never kills the wrong process across 1,000 iterations.

### 5.4 System Info

Firmware/BIOS, board, CPU (model, topology, cache, features), memory modules (size, speed, form factor, type — subject to the DMI rule), GPUs, disks (model, serial, firmware, SMART health, temperature), network adapters, battery, OS and kernel, and the app's own build and the "running as" identity. A **Copy report** button produces a redacted, deterministic text block suitable for a bug report, and an **Export JSON** button the full one.

**Acceptance:** the redacted report contains no serial number, machine id, MAC address, username, SSID or path unless the user opts in per field.

### 5.5 Startup apps

Sources: XDG autostart entries (`.desktop` in `/etc/xdg/autostart` and `~/.config/autostart`), systemd user units wanted by `default.target`, macOS LaunchAgents/Daemons, Windows `Run`/`RunOnce` keys (HKLM/HKCU, 32/64-bit) and Startup folder. Show the command, the source path, the enabled state and the owning package where known.

**Enable/disable** writes a reversible `Hidden=true`/`X-GNOME-Autostart-enabled=false` for XDG entries, `systemctl --user disable`, `launchctl disable`/`bootout`, and the documented registry value for Windows — never deletes anything. Every change is journalled with an undo action, and the UI says exactly which file or key it touched.

**Acceptance:** disabling and re-enabling returns the system to byte-identical configuration (verified by test).

### 5.6 Users

Local sessions (who, tty/display, login time, idle), per-user aggregates (processes, memory, CPU), and the ability to filter Processes to a user. Read-only. Remote sessions named distinctly.

### 5.7 Services

Linux: systemd units via D-Bus (`ListUnits`, `StartUnit`, `StopUnit`, `RestartUnit`) with the polkit dialogue the desktop normally shows; if `libsystemd`/D-Bus is unavailable, the page states that and offers CLI guidance instead of failing silently. macOS: `launchctl` `print`/`kickstart` with explicit permission prompts. Windows: SCM via a helper (enumerate, start, stop, restart) with the standard UAC prompt.

Every verb shows the unit name, description and current state in the confirmation; failures are surfaced verbatim (the system's own error text) rather than summarised.

### 5.8 Power & Frequency

Package and per-core power (RAPL on Linux, vendor SDKs on Windows, `powermetrics`-equivalent where available on macOS), per-core frequency (reported and effective), governor/EPP, thermal pressure state, battery (charge, power, cycles, time remaining), and an **energy impact** ranking (§9.4).

Unavailable sources name their grant: on Linux, "powercap is root-only; see docs/linux-powercap" with a copyable udev rule.

### 5.9 Connections

A socket table from `AF_INET/AF_INET6/UNIX` with protocol, local/remote address and port, state, and **owning process** by joining socket inodes to `/proc/<pid>/fd` — falling back to `unavailable (needs CAP_NET_ADMIN)` rather than guessing. Views: all, listening, established, by process, **exposed** (listening on non-loopback), and a "new in the last minute" diff view. Lookup of service names from a bundled IANA registry (offline).

**Acceptance:** a listener started and stopped mid-session appears and disappears; a socket whose owner cannot be resolved says so.

### 5.10 Installed Apps

Package sources: dpkg/rpm, Flatpak, Snap, Homebrew, `/Applications` bundles, and the Windows uninstall registry. Columns: name, version, vendor, source, installed size, last used (where the OS records it), and the update channel. **Uninstall** shows the exact command it will run and requires confirmation; it executes that command, never a shell string built from a package name.

### 5.11 Disk Space

A scanner that walks a chosen root without following symlinks, staying on one filesystem unless told otherwise, skipping a configurable exclude list, and reporting: per-directory totals, a treemap, a largest-files list, and the scan's own cost. Scans are cancellable, resumable per level, and **never** run with privileges by default. A history of completed scans shows growth between runs.

**Safety:** a "delete" action does not exist. The tool can reveal a path in the OS file manager; deletion stays in the user's hands.

### 5.12 Benchmarks

Deterministic, offline, local-history benchmarks: CPU single-thread and multi-thread (fixed integer/float workloads with a checksum), memory bandwidth (read/copy), disk sequential read/write and 4K random IOPS on a chosen file (with a size the user picks and a clear warning), and a network loopback sanity check. Every result records the machine fingerprint (redacted), the app version and the workload hash, so scores are only compared like-for-like. **No upload, ever**; sharing is export-only.

### 5.13 Recorder

See §7.

### 5.14 Fleet

See §8.4.

### 5.15 Advisor

See §9.

### 5.16 Settings

| Group | Settings |
| --- | --- |
| Sampling | base interval (0.5/1/2/5 s), fast mode (up to 30 Hz for CPU/GPU), history length (1/5/30/60 min in memory) |
| Units | bytes/bits per second, IEC/SI, °C/°F, watts vs BTU/h |
| Appearance | theme, tint, saturation, text scale 100–200 %, high contrast, reduce motion, dense mode |
| Interface | start minimised, close to tray, always-on-top popout, rows highlighted by state |
| Recorder | ring buffer on/off and size, auto-record on high load, retention |
| Remote | listen address, pairing, paired devices, read-only enforcement |
| Privacy | what is stored locally, where, how to wipe it; network toggles |
| Advanced | provider paths, per-provider timeouts, export diagnostics |

All settings are plain JSON on disk with a documented schema, so they can be provisioned by an admin.

## 6. Actions and safety

An action is a request with an identity, a confirmation policy, an execution mode and an audit record. The daemon exposes `POST /v1/actions` with a typed body; it revalidates identity, refuses if the target vanished or changed, and returns the platform's own error text on failure.

| Action | Linux | Windows | macOS | Confirmation |
| --- | --- | --- | --- | --- |
| end task | SIGTERM | `TerminateProcess` | SIGTERM, then SIGKILL after grace | typed name for system-owned |
| force kill | SIGKILL | terminate + suspend | SIGKILL | yes |
| suspend / resume | SIGSTOP / SIGCONT | `NtSuspendProcess` | SIGSTOP / SIGCONT | no |
| priority | `setpriority` | `SetPriorityClass` | `setpriority` | no |
| service start/stop | systemd D-Bus | SCM | `launchctl` | yes |
| startup toggle | file edit | registry value | plist edit | yes + undo |

Everything is journalled to `~/.local/state/vernier/audit.jsonl` (or the platform equivalent) with timestamp, action, target identity and result.

## 7. Recorder

**Always-on ring buffer** in memory (default 5 minutes at 1 Hz for ~120 series ≈ 30 MB) so "replay the last five minutes" needs no prior decision. Explicit recordings are longer and persisted.

**Format `vntr` (v1)** — a single file, streamable, crash-safe:

```
magic "VNTR\x01" | header_len u32 | header JSON | frames...
header: {schema, app, platform, host_redacted, started_at, series:[{id, unit, kind, scale}], plugins}
frame : {t_mono u64, t_wall u64, flags u8, payload_len u32, payload}
payload: LEB128 varint deltas per series, null bitmap for gaps
```

Append-only, each frame CRC-tagged, `flags` records events (pause, resume, sleep, provider failure, user annotation). Replay is the same renderer as live mode with a time cursor, so there is no second UI to keep in sync. Export to JSONL/CSV/Parquet optional (Parquet behind an optional dependency).

**Acceptance:** a trace recorded on Linux opens on Windows; a 24-hour recording at 1 Hz with 120 series is ≤ 40 MB; corrupting any single frame loses that frame only; a sleep event is replayed as a visible gap with its duration.

## 8. Remote and fleet

### 8.1 Posture

Localhost by default. `--listen` or a settings toggle enables the listener; the console warns until HTTPS-with-pairing is configured. There is no vendor relay: LAN or the user's own tailnet/VPN.

### 8.2 Pairing

1. The daemon advertises `_vernier._tcp` via mDNS **only** while a pairing window is open (default 3 minutes), under the machine's display name.
2. The client connects and both sides derive a **short authentication string** from an ephemeral X25519 exchange plus both nonces; each screen shows six characters; the user compares and confirms.
3. On confirmation each side stores a long-term device key, pins the peer's public key, and closes the window.
4. Sessions use TLS 1.3 with self-signed certificates pinned to the stored keys; no CA, no cloud, no password in traffic.
5. Revocation is one click per peer; a revoked peer's key is refused and logged.

### 8.3 Read-only by default

A paired phone/browser is read-only. Writable access is a separate, explicit grant per device, and destructive verbs require a second confirmation in the session. The remote API never exposes settings, pairing or provider installation to a read-only peer.

### 8.4 Fleet

The console can hold many paired daemons. `/fleet` shows a card per machine with the same mini-panels as Summary, sorted by a chosen metric, with a text filter and a "only show degraded" toggle. There is no central server and no aggregation endpoint: each card polls its own daemon. A CLI `vernier fleet --file fleet.json` does the same for scripts, emitting one JSON document.

## 9. Advisor (attribution, not chatbot)

The purpose is to answer *"who is responsible for this symptom?"* without hallucination.

### 9.1 Signals

| Signal | Detection |
| --- | --- |
| CPU saturation | sustained busy > 85 % for ≥ 10 s, with the top contributor |
| Thermal throttling | effective clock < 70 % of reported max while temperature ≥ threshold |
| Memory pressure | PSI full > 10 %, or compression/swap-in sustained |
| Disk contention | queue depth > 4 or await > 40 ms sustained, named device + top process |
| Network loss | retransmits, errors, or a rate collapse on one interface |
| Energy drain | watts above a rolling baseline, ranked by per-process attribution where available |
| Runaway process | one process > 50 % CPU for ≥ 30 s, or RSS growth > 200 MB/min |

### 9.2 Output

A ranked card: symptom, window, the responsible process/device if identified, the evidence (the series and samples), the confidence (rule strength, not a fake percentage), and a suggested next step that is a *link inside the app* (e.g. open Processes filtered to that PID, open Connections on that port). Every card is reproducible from the trace: it cites sample ranges.

### 9.3 Optional model

If — and only if — a user configures a local inference endpoint, the Advisor can send the *previewed* snapshot (same redaction rules as the export) to that endpoint. Cloud endpoints are not supported by default; a build flag is required and the UI says so. Process names are opt-in. The preview is the consent screen.

### 9.4 Energy impact

Per-process energy cannot be measured directly on general-purpose hardware. Our definition, published in the UI's methodology link: **energy impact = share of CPU time × package power + share of disk I/O × device power estimate + share of network × NIC power estimate**, normalised so the sum equals the measured package power when that reading is `ok`. Where package power is unavailable the column says `unavailable`, and we do not ship an invented unit. (The original's normalisation is not published; ours is.)

## 10. CLI and API

```
vernier summary                 # one JSON document (default), --text for a table
vernier watch --interval 1s --metrics cpu.package.busy_pct,memory.used_bytes
vernier processes --top 20 --sort cpu --json
vernier process 1234 --tree     # identity, resources, sockets, files
vernier connections --listening --exposed
vernier record --duration 60s -o spike.vntr
vernier replay spike.vntr --at 00:00:31
vernier tail --follow           # JSONL stream of readings
vernier doctor                  # provider health, permissions, kernel features
vernier bench cpu --json
vernier fleet --file fleet.json
```

Exit codes: `0` ok, `2` usage, `3` no such target, `4` permission denied, `5` provider degraded (partial output still printed), `6` unsupported platform.

HTTP: `GET /v1/series`, `/v1/processes`, `/v1/process/:key`, `/v1/system`, `/v1/providers`, `/v1/trace`, `POST /v1/actions`, `POST /v1/recordings`, `GET /v1/pair`. JSON Schema is committed in `schemas/` and versioned; breaking changes bump `/v2`. Prometheus exposition at `/metrics` is opt-in and labelled by machine and device.

## 11. Extensibility

### 11.1 Providers

A provider is an executable with a manifest:

```json
{ "id": "org.example.nvml", "name": "NVIDIA telemetry", "api": 1,
  "platforms": ["linux", "windows"],
  "metrics": ["gpu.utilization_pct", "gpu.memory.used_bytes"],
  "permissions": ["dlopen:libnvidia-ml.so.1"],
  "interval_hint_ms": 1000, "exec": "./nvml-provider" }
```

Transport is newline-delimited JSON-RPC 2 over stdio: `initialize`, `describe`, `sample`, `cancel`, `shutdown`. The daemon enforces a deadline per `sample`, kills and restarts a provider that exceeds it three times, and renders `error` for its metrics while others continue. Providers declare permissions; the UI shows them before enabling; a provider never inherits elevation. A registry file (`providers/registry.json`) lists known providers with hashes, but nothing is installed automatically.

### 11.2 Skins

Our native format is JSON with a documented schema and the same philosophy as the original's published guide: a skin is data, cannot reach outside its folder, cannot name a URL, and unknown tokens are dropped rather than fatal. We additionally ship an **importer** for the documented TMOG skin format so users can bring existing skins; it is best-effort, non-normative, and documented as such ([legal note](08-risks-and-legal.md#4-third-party-formats)).

## 12. Accessibility, i18n, theming

- WCAG 2.2 AA for the console: contrast, focus order, no keyboard traps, target sizes, error identification.
- Meters and graphs expose ARIA `meter`/`img` roles with a text summary ("CPU busy 34 percent, 8 of 24 segments, scale 0–100").
- Text scale 100–200 % without clipping; high-contrast theme; `prefers-reduced-motion` disables bloom and easing.
- Full keyboard operation, a command palette, and an optional Vim binding set (`j/k`, `gg/G`, `/`, `dd` on tables) — a repeated request in the original's tracker [D].
- i18n from day one: ICU messages, no concatenated strings, plural rules, `Intl` number/date formatting, RTL-safe layout. Ship English; the community supplies the rest.

## 13. Budgets and definitions of done

| Budget | Target |
| --- | --- |
| Daemon RSS at 1 Hz, 120 series | ≤ 60 MB |
| Daemon CPU at 1 Hz | ≤ 1.5 % of one core |
| First console frame | ≤ 300 ms after navigation |
| Sample jitter | p99 ≤ 25 % of interval |
| Action latency (kill/priority) | ≤ 50 ms after confirmation |
| Trace size | ≤ 40 MB per 24 h at 1 Hz |
| Cold build | ≤ 90 s |

A page is done when: all five states are implemented with copy; every reading has provenance; its acceptance test passes in CI; it is keyboard-complete; it exports; and its metrics appear in the API and CLI.

## 14. Deliberate differences from the original

| # | Original | Ours | Reason |
| --- | --- | --- | --- |
| 1 | Pro gate on six destinations + recorder | All free | The point of the project |
| 2 | Closed source | Apache-2.0, reproducible | Auditability |
| 3 | Three native UIs | One console + native shells later | Reach and maintainability; native metrics still required |
| 4 | ~60 Hz display-cadence animation | Sample-true readouts, ≤120 ms visual easing | A meter implies measurement; we animate paint, not data |
| 5 | `.tmogtrace`, unpublished | `vntr`, specified and versioned | Portability, long-term readability |
| 6 | iPhone viewer, Pro, Mac-first | Any browser, any platform, read-only pairing | Fleet and headless reality |
| 7 | No scripting surface | CLI + HTTP + Prometheus | Operators alert on numbers |
| 8 | Skins only (data) | Skins **and** providers (code, sandboxed) | Vendor sensors, containers, NAS |
| 9 | Env-var sampling log | Always-on recorder + provider health page | Diagnose without a support round-trip |
| 10 | "Energy impact" normalisation unpublished | Published formula, `unavailable` when power is | Honesty about a derived metric |
| 11 | Update check on launch | No automatic network request | Privacy by default |
| 12 | AI Advisor prototype, local inference | Rule engine first, model optional and local | Attribution should be deterministic |

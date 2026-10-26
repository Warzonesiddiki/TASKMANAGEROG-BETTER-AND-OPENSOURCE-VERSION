# 05 — Architecture

## 1. Constraints that shape the design

| Constraint | Consequence |
| --- | --- |
| Must be buildable and runnable **in this environment** (Linux, Node 22, Python 3.11, gcc 12, no Qt, no Rust, no GUI session) | The first deliverable is a daemon + browser console + CLI, all buildable here |
| Must run on **Windows and macOS** with the same contract | Platform access is behind a provider interface, never `if (platform)` in the core |
| Sensors need APIs that a managed runtime cannot call (SMC, PDH, DXGI, NVMe ioctl, D-Bus) | Native code lives in **small sidecar providers**, not in the core |
| Users expect a native-feeling instrument | One excellent console, wrapped by a native shell later; no second UI to drift |
| Auditable and reproducible | Deterministic builds, pinned dependencies, SBOM, no post-install scripts |
| No telemetry, no accounts | No backend services at all; the site is static |

## 2. ADR-001 — the stack

**Decision: a TypeScript/Node daemon (`vernierd`) + React console + provider sidecars, with an optional Tauri desktop shell.**

| Option | Buildability here | Cross-platform | Footprint | Sensor access | Build speed | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| **TS core + React console + sidecars** | ✅ Node 22 present | ✅ | ⚠️ ~50–80 MB RSS daemon; console only when open | ✅ via sidecars | ✅ fastest | **Chosen** |
| Rust core + Tauri | ❌ no toolchain, long CI builds | ✅ | ✅ ~15 MB | ✅ in-process | ⚠️ slow to iterate | Revisit for 2.0 core |
| C++20 + Qt 6 | ❌ no Qt, heavy toolchain | ⚠️ three UIs | ✅ | ✅ | ❌ slowest | Rejected as first step |
| Go daemon + web console | ❌ no toolchain present | ✅ | ✅ | ✅ cgo sidecars | ✅ | Runner-up; no ecosystem benefit over TS here |
| Swift/WinUI/WPF natives | ❌ | ❌ one at a time | ✅ | ✅ | ❌ | Rejected: three codebases |

**Why this is defensible, not lazy.** The expensive, durable part of TMOG is not its UI toolkit; it is the metric semantics and the per-OS sensor knowledge. This architecture puts the *contract* in one testable core, isolates the per-OS sensor code into small native sidecars that any language can implement, and spends the saved UI effort on remote access, scripting and accessibility. If the console later proves too heavy, it can be replaced without touching a single metric definition — that is precisely what the provider protocol buys.

**Honest costs.** A Node daemon uses more memory than a C++ one, and a web console renders slower than a native table at 60 Hz. Mitigations, all specified: sampling and storage are allocation-light and off the render path; the console is a static bundle served from disk with no framework runtime on the sampling path; a Tauri shell replaces the browser when a "real app" is wanted; and a TUI (`vernier watch`) covers the low-footprint case. The performance budget in §10 is a hard gate, not an aspiration.

## 3. Process and data flow

```
┌─────────────────────────────── vernierd ───────────────────────────────┐
│                                                                        │
│  Scheduler (monotonic, fixed-rate, priority lanes)                     │
│    fast 1–30 Hz: cpu, memory, gpu, network, storage                    │
│    slow 1/5 s:   processes, connections, apps                          │
│    on demand:    disk scans, benchmarks, services                      │
│         │                                                              │
│         ▼                                                              │
│  Provider host ──spawn/restart/deadline──► sidecars (JSON-RPC/stdio)   │
│         │                                   linux.procfs               │
│         │                                   linux.sysfs                │
│         │                                   windows.pdh  …            │
│         ▼                                                              │
│  Normaliser ── units, states, provenance, identity──► Ring buffers     │
│         │                                              (per series)    │
│         ├──────────────► Recorder (always-on, vntr frames)             │
│         ├──────────────► Rules engine (Advisor signals)                │
│         └──────────────► API layer                                     │
│                            HTTP/JSON  ·  SSE stream  ·  Prometheus     │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ localhost:7420 (token on first run)
        ┌──────────────────────────┼───────────────────────────┐
        ▼                          ▼                           ▼
  React console              CLI (vernier)               Remote peers
  (browser / Tauri)          JSON, watch, doctor         (paired, TLS-pinned)
```

The console and the CLI are both plain API clients. That is what makes the remote view free to build rather than a separate product.

## 4. Repository layout

```
packages/
  core/            metric registry, units, reading envelope, ring buffers, gap logic
  daemon/          scheduler, provider host, API, recorder, rules engine, pairing
  console/         React app, theme tokens, meters, graphs, tables
  cli/             argument parsing, JSON/text renderers, exit codes
  shared/          schemas (JSON Schema), generated TS types, error taxonomy
providers/
  linux-procfs/    TS over fs                    (M1)
  linux-sysfs/     TS over fs                    (M1)
  linux-native/    C++ sidecar: NVMe SMART, ioctl (M3)
  windows-native/  C++ sidecar: PDH, WMI, DXGI, SCM (M4)
  macos-native/    Swift sidecar: IOKit, SMC, launchd (M4)
  registry.json
schemas/           v1 JSON Schema: reading, process, connection, trace, skin
tests/
  fixtures/        captured /proc, sysfs, sysctl dumps, with provenance READMEs
  golden/          recorded traces for regression
  e2e/             Playwright against the console
docs/              this dossier
site/              static site generator input (M6)
```

## 5. The provider protocol

Providers are executables, so a provider can be TypeScript (fast to write), C++ (fast to run), Swift, or a third party's binary. The daemon speaks newline-delimited JSON-RPC 2.0 over stdio.

```jsonc
→ {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"api":1,"locale":"en"}}
← {"jsonrpc":"2.0","id":1,"result":{"id":"linux.procfs","metrics":[...],"platforms":["linux"]}}
→ {"jsonrpc":"2.0","id":2,"method":"sample","params":{"ids":["cpu.package.busy_pct"],"window_ms":1000}}
← {"jsonrpc":"2.0","id":2,"result":{"readings":[{"id":"cpu.package.busy_pct","value":34.2,"state":"ok",...}]}}
```

Rules: one in-flight `sample` per provider; a hard deadline (default 80 % of interval); three consecutive timeouts trip a circuit breaker with exponential backoff and a named degradation in the UI; a provider that crashes is restarted with a crash-loop budget; a provider never receives the daemon's privileges it did not declare.

**Why this shape:** it makes the "one hung sensor freezes the whole app" class impossible by construction — the exact class that dominates the original's bug tracker.

## 6. Sampling and storage

- One scheduler thread per priority lane, `setTimeout`-driven with a monotonic deadline and catch-up clamping (never more than one skipped tick).
- Series are typed arrays: `Float64Array` values + `Uint8Array` states + `BigInt64Array` monotonic timestamps, ring-allocated. 120 series × 5 min at 1 Hz ≈ 4 MB, not 30 MB, if states are packed.
- The recorder consumes the same rings; nothing re-samples for a recording.
- Persistence (recordings, benchmarks, scan history, settings, audit) is SQLite in WAL mode by default, with a JSON fallback for read-only filesystems.

## 7. API

- `GET /v1/stream` — SSE, one event per generation, payload is the delta since the last generation for the visible series only (the console tells the daemon what it is showing).
- `GET /v1/series?ids=…&from=…&to=…` — history for graphs and export.
- `GET /v1/processes`, `/v1/process/:pid/:start`, `/v1/system`, `/v1/providers`, `/v1/recordings`, `/v1/fleet`.
- `POST /v1/actions`, `/v1/recordings`, `/v1/pair`.
- `/metrics` — Prometheus, opt-in.
- Every response carries `generation`, `server_time` and a `degraded[]` array naming providers that are not `ok`.

Versioning: additive fields are minor; removed or re-typed fields require `/v2`. Schemas live in `schemas/` and are the source of generated types.

## 8. Console

- React 19 + TypeScript, no UI framework dependency; a design-token sheet (`--vg-*` custom properties) drives themes and text scale.
- Graphs on `<canvas>` with a single draw loop per visible chart, decoupled from React state; React owns layout and tables, the canvas owns pixels. This is how the console stays smooth when the daemon is at 30 Hz.
- Tables are virtualised with a fixed row height and windowed rendering; sorting and filtering happen in the daemon when datasets are large (connections, disk scans).
- State: a small store with per-destination subscriptions, so a Summary update does not re-render Processes.
- Accessibility: ARIA table semantics, focus rings, live regions for degraded states (announced once, not per sample), text-scale via root font-size.

## 9. Security model

| Surface | Control |
| --- | --- |
| Loopback API | Random 32-byte token written to `~/.config/vernier/token` (0600) at first run; required header; `Origin` allowlist; no CORS wildcard |
| Browser console | Strict CSP (no inline scripts, no remote origins); the console is served from the daemon, so no network fetch is needed |
| Remote listener | Off by default; TLS 1.3 with pinned device keys; read-only unless writable is explicitly granted |
| Pairing | X25519 + six-character SAS, three-minute mDNS window, replay-resistant nonces |
| Providers | Declared permissions shown before enabling; no elevation; optional sandbox (bubblewrap/seccomp on Linux, AppContainer on Windows) |
| Actions | Identity revalidation, confirmation policy, audit log |
| Updates | Manual, signed artefacts, published SHA-256; no background download |
| Secrets | Never stored: no accounts, no licence, no tokens for third-party services |

## 10. Performance budget and how it is met

| Budget | Technique |
| --- | --- |
| Daemon RSS ≤ 60 MB | Typed-array rings, no per-sample object churn, sidecars own heavy native state |
| ≤ 1.5 % CPU at 1 Hz | Batched reads, `pread` over `readFile`, parse only changed files, slow lane for expensive sources |
| First frame ≤ 300 ms | Static bundle served from disk, no SSR, deferred chart init, skeleton from the first `/v1/system` call |
| p99 jitter ≤ 25 % | Monotonic deadlines, worker threads for parsers, provider deadlines |
| 60 fps charts, 1–30 Hz data | Canvas draw decoupled from sampling; easing only in paint |

Budgets are enforced in CI with a benchmark harness that fails the build on regression beyond 10 %.

## 11. Testing and CI

| Layer | Tool | Gate |
| --- | --- | --- |
| Unit + fixtures | `node:test` | 100 % of parsers have a malformed-input case |
| Semantics | custom harness | state transitions and gaps asserted |
| Golden traces | replay harness | CPU/mem/disk/net within 1 % of recorded truth |
| E2E | Playwright | every destination in all five states, keyboard-only path |
| A11y | axe-core | zero serious violations |
| Perf | benchmark suite | budgets in §10 |
| Matrix | GitHub Actions | ubuntu-latest, windows-latest, macos-latest; Node 22 and 24 |
| Reproducible | `npm ci --ignore-scripts`, lockfile, deterministic bundle | two builds, identical hashes |

## 12. Packaging and release

- Daemon: Node 22 Single Executable Application, or a `bun build --compile` artifact where available; assets embedded.
- Linux: AppImage, `.deb`, `.tar.gz` (x64 + arm64); Windows: MSI/EXE via WiX or Inno; macOS: `.dmg` + notarised app bundle; plus winget, Scoop, AUR, Homebrew formulas generated from the same release metadata.
- Each release publishes SHA-256, an SBOM (CycloneDX), a signed git tag, and a short release note written from the changelog.
- No post-install scripts, no services installed, no auto-update daemon.

## 13. The site

A static generator over `docs/` plus a download page driven by a checked-in `releases.json` (version, platform, artefact, size, SHA-256, date). No analytics, no cookies, no third-party fonts. The privacy page states exactly what the daemon does on the network, and it can be checked against the source — a claim the original cannot make.

## 14. Migration path

If the Node core ever becomes the wrong choice, the contract survives: metric ids, reading envelope, provider protocol and API are versioned documents. A Rust or C++ daemon can implement them, the console stays, and users notice nothing but the footprint. Writing those documents first is the reason this dossier exists.

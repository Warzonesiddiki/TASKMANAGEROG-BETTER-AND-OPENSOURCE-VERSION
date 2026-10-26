# 07 — Roadmap

*Estimates are "focused person-days" for one experienced engineer who knows the codebase. They exclude waiting on hardware, review latency and packaging bureaucracy. The workstreams are separable: a second person working on console/providers in parallel roughly halves the calendar time.*

## Phase map

| Milestone | Theme | Est. | Gate to pass |
| --- | --- | --: | --- |
| **M0** | Research, specification, architecture, naming | **done** | This dossier is reviewable and every claim is sourced |
| **M0b** | Observation programme against a licensed copy | 3 | Observation sheets committed; no assets, no binary analysis needed to proceed |
| **M1** | Linux core + console: the instrument exists | 32 | Summary → Processes → culprit in under 60 s; budgets met |
| **M2** | The machine: actions, startup, services, users, connections, disk space | 24 | Every action identity-safe and reversible where it claims to be |
| **M3** | Insight: recorder/replay, power, installed apps, benchmarks | 20 | A recorded spike replays identically on another OS |
| **M4** | Windows + macOS parity | 40 | Same metric ids, same states, same console, real hardware verification |
| **M5** | Beyond: remote, fleet, API, provider SDK | 24 | A paired phone is read-only; a third-party provider ships without a fork |
| **M6** | Product: shells, packaging, accessibility, i18n, 1.0 | 20 | Six installation channels, WCAG 2.2 AA, signed reproducible artefacts |

**Total ≈ 160 focused days for M1–M6** (plus 3 for M0b): ≈ 8 months solo, ≈ 4 months with two people.

## M0 — Research and planning ✅

Delivered: this dossier (`docs/00`–`09`), the reproducible issue analysis (`docs/research/`), the fetch/analyse scripts, the repository front page, and the naming shortlist.

Exit criteria, all met: every factual claim about the original has a source and a date; the specification is independent of any copied text or asset; the stack decision has alternatives and costs; the roadmap has acceptance tests.

## M0b — Observation programme

Runs wherever a legitimately licensed TMOG copy and the reference hardware are available. Output is committed observation sheets, not screenshots. The ten experiments are specified in [01 §5](01-reverse-engineering-method.md#5-the-observation-programme-what-to-do-when-a-licensed-copy-is-available).

| # | Experiment | Output |
| --: | --- | --- |
| 1 | Cold-start census of states and wording | State machine table (restated in our words) |
| 2 | Cadence map per panel | True sampling vs animation per destination |
| 3 | Sensor ablation (hwmon, powercap, DMI, GPU) | Availability state matrix |
| 4 | PID-reuse identity test | Confirmation of identity semantics |
| 5 | 60-second suspend gap test | Gap behaviour reference |
| 6 | Self-cost measurement | External reference for our budgets |
| 7 | Recording experiment (single variable) | Notes on size/entropy; no format compatibility assumed |
| 8 | Skin conformance (documented tokens only) | Conformance case list |
| 9 | Remote pairing observation | Confirmation of SAS, window, read-only |
| 10 | Update/licence request timing | Confirmation of the published privacy behaviour |

## M1 — The instrument (Linux)

| # | Work | Days | Acceptance |
| --: | --- | --: | --- |
| 1 | Monorepo scaffold, TypeScript config, lint, CI, release skeleton | 2 | `npm ci && npm start` serves the console |
| 2 | Metric registry, units, reading envelope, JSON Schemas, generated types | 2 | 60 metrics described; schema validates a sample envelope |
| 3 | Scheduler (monotonic lanes) + provider host (JSON-RPC, deadlines, circuit breaker) | 3 | A deliberately hanging test provider degrades one tile and is named |
| 4 | `linux.procfs`: CPU, memory, PSI, loadavg, uptime, per-process basics | 4 | Fixtures for every file; totals match `times()` within 1 % |
| 5 | `linux.sysfs`: topology, P/E class, frequencies, hwmon, block, net devices | 4 | Dual-socket and hybrid fixtures; sensor precedence locked by tests |
| 6 | Ring buffers, gap model, sleep detection, generation counter | 2 | Suspend test produces one labelled gap, no interpolation |
| 7 | Console shell: layout, tokens, six themes, command palette | 2 | Keyboard-only navigation; contrast AA |
| 8 | Meters and graphs on canvas (scales, bloom, voids, crosshair) | 3 | 30 Hz data renders at 60 fps; void band labelled |
| 9 | **Summary** page | 2 | Acceptance test in [03 §5.1](03-product-spec.md#51-summary) |
| 10 | **Performance** page (CPU, memory, disk, network) | 3 | Device add/remove handled without reload |
| 11 | **Processes** page + detail pane + filter/sort/follow | 2 | Identity-safe selection; 100 k-row scroll stays at 60 fps |
| 12 | **System Info** page + redacted report + export | 1 | Redaction test passes |
| 13 | CLI: `summary`, `watch`, `processes`, `doctor`; exit codes | 2 | JSON matches schema; `doctor` explains every non-`ok` provider |

**Stop/go gate.** If daemon RSS > 120 MB at 1 Hz, or first frame > 600 ms on the reference laptop, pause M2 and either (a) move the hot path to a native sidecar, or (b) ship the TUI as the primary surface and treat the console as optional. Do not proceed on the assumption that it will get faster later.

## M2 — The machine

| # | Work | Days |
| --: | --- | --: |
| 1 | Action framework: identity revalidation, confirmation policy, audit log, platform verbs for processes | 4 |
| 2 | **Startup apps** with reversible toggles and provenance | 3 |
| 3 | **Services** via systemd D-Bus, polkit-aware, graceful when absent | 3 |
| 4 | **Users** and session joins | 2 |
| 5 | **Connections** with owner join, `denied` handling, exposed view | 4 |
| 6 | **Disk Space** scanner: excludes, mount boundaries, treemap, history | 5 |
| 7 | Tests: action reversibility, socket attribution, scanner cancellation | 3 |

## M3 — Insight

| # | Work | Days |
| --: | --- | --: |
| 1 | `vntr` recorder: always-on ring, explicit recordings, crash-safe frames | 3 |
| 2 | Replay surface sharing the live renderer; scrub, annotate, export | 3 |
| 3 | Power: RAPL with wraparound, battery, energy impact formula + methodology page | 4 |
| 4 | **Installed Apps** across package managers, safe uninstall executor | 3 |
| 5 | **Benchmarks** with recorded fingerprints and local history | 4 |
| 6 | Tests: cross-platform replay, trace corruption, energy maths | 3 |

## M4 — Windows and macOS

| # | Work | Days |
| --: | --- | --: |
| 1 | `windows-native` sidecar: PDH, WMI, DXGI, SCM, SMART, battery | 12 |
| 2 | `macos-native` sidecar: mach, IOKit, SMC, launchd, power sources | 12 |
| 3 | Console parity: fonts, HiDPI canvas, OS-native menus via Tauri shell | 6 |
| 4 | GitHub Actions matrix on real runners; three reference machines | 6 |
| 5 | Per-OS setup docs (privileges, sensors, known gaps) | 4 |

**Ambition test for this milestone:** the same metric id must produce `ok` on the same class of hardware on all three platforms, or a *documented* `unsupported`/`denied` with the grant that would fix it. Divergence without documentation is a bug.

## M5 — Beyond

| # | Work | Days |
| --: | --- | --: |
| 1 | Pairing: X25519 + SAS, mDNS window, pinned TLS, revocation | 5 |
| 2 | Remote console, read-only enforcement, per-device writable grant | 4 |
| 3 | **Fleet** view and `vernier fleet` | 3 |
| 4 | Prometheus exporter, JSONL tail, OTLP (optional module) | 2 |
| 5 | Provider SDK: docs, sample provider, manifest validation, sandbox profile | 5 |
| 6 | Security review: threat model, dependency audit, fuzzing of parsers | 3 |
| 7 | Tests: pairing, replay, revocation, provider abuse | 2 |

## M6 — Product

| # | Work | Days |
| --: | --- | --: |
| 1 | Tauri desktop shell (tray, popout, global shortcut, single instance) | 5 |
| 2 | Packaging: AppImage, deb, tar.gz, Flatpak, AUR, winget, Scoop, brew, MSI, DMG | 6 |
| 3 | Accessibility audit to WCAG 2.2 AA, screen-reader pass, high-contrast theme | 2 |
| 4 | i18n extraction and two community locales | 2 |
| 5 | Site: downloads from `releases.json`, checksums, SBOM, release notes, docs | 3 |
| 6 | 1.0 soak, release, announcement, post-mortem | 2 |

## Working conventions

- **Trunk-based** development; short-lived branches; PRs under 400 changed lines where possible.
- **Conventional commits**; `CHANGELOG.md` generated; semantic versioning; `DCO` sign-off, no CLA.
- **ADRs** in `docs/adr/NNN-title.md` for any decision that changes a contract.
- **Changesets** for anything user-visible; release notes are written for users, not for git.
- **No screenshot-driven PRs.** A behaviour change cites an observation sheet or an issue, never "that's how the original does it".
- **Issue templates** for bug (with `vernier doctor` output), provider request (with manifest sketch) and feature (with the honesty test: what does it show when the data is unavailable?).
- **Review rule:** a PR that adds a metric without a fixture and a state test is not reviewable.

## Sequencing rationale

The ordering is chosen to make the *promise* demonstrable as early as possible. M1 proves the honesty model and the performance budget on the only platform available here. M2 proves that the tool can *act*, not just watch, which is where a monitor becomes a task manager. M3 proves durability (recording survives the moment). M4 is the expensive parity leap and is deliberately after the contract is frozen, so no Windows-specific decision can leak into the model. M5 is what a closed product cannot copy cheaply. M6 is polish with a deadline.

## What could change this plan

| Trigger | Response |
| --- | --- |
| Footprint gate fails at M1 | Native core sidecar or TUI-first pivot |
| Sensor coverage below 80 % on reference hardware after M2 | Invest in a provider registry and vendor sponsorships before M4 |
| TMOG goes open source | Re-evaluate: contribute providers upstream, keep the remote/API/plugin layer as the differentiator |
| A strong OSS competitor appears | Differentiate harder on auditability and fleet; do not race on destinations |
| Dave Plummer objects publicly | Respond with the clean-room record; change the name if asked; never argue in public |

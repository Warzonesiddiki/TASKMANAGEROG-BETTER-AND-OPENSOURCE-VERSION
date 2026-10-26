# 00 — Executive summary

*Written 2026-10-26. Every factual claim here is dated and sourced in [09 — Evidence log](09-evidence-log.md).*

## The situation

[TMOG (Task Manager OG)](https://tmog.org/) is a closed-source, cross-platform system monitor by Dave Plummer, the engineer who wrote the original Windows Task Manager in 1996. Its **1.1.0** build shipped on **2026-10-26**, the same day this dossier was written, with published SHA-256 sums for macOS, Windows x64/ARM64 and Linux x64/ARM64.

Four facts shape everything that follows.

1. **The product's *requirements* are unusually well documented in public.** The site states the information architecture (twelve destinations), the measurement philosophy ("unsupported means unsupported", "a stopped measurement leaves a gap"), the packaging matrix, the release notes, the privacy behaviour, the Linux privilege model (`powercap`, SMBIOS DMI), the AMD sensor story, and — remarkably — a complete, versioned **JSON skin format** for the popout, published so users can write skins.
2. **The product's *failure modes* are documented too.** The public tracker contains **1,548 reports** between 2026-07-31 and 2026-10-26: 58 % bugs, 38 % feature requests, led by temperature/thermals (160 titles), licensing/updates (133), process-table behaviour (128), UI/i18n (120) and GPU readings (82), with crashes and data-quality complaints spread through the rest. See [the generated analysis](research/issues-analysis.md).
3. **The source is not open and there is no sign it will be.** A feature request to open-source it (#1568) is still open. The upstream repository URL embedded in the shipped Linux build returns 404 and no public source repository exists (per third-party static analysis, re-checked here).
4. **The paid tier is thin and separable.** Pro ($39.95, three machines, one-time, via Lemon Squeezy) is Flight Recorder, Power & Frequency, Connections, Installed Apps, Disk Space and Benchmarks — plus an iPhone remote view and an AI Advisor prototype. The free tier is already a complete monitor.

## The strategic reading

TMOG's moat is **not its feature list**. Its moat is (a) an honest measurement model that users now expect, and (b) three hand-built native front ends. The feature list is documented, the model can be copied as *behaviour*, and the native craft is expensive to match — so we should not try to match it where it does not matter.

**Do not compete on "more native than thou".** Compete on the things a closed, single-machine, paywalled product structurally cannot do:

- **Auditability.** Every reading traces to a metric id, a provider, a source path on the machine, a timestamp and an availability state. A user can ask "why does this say 34 °C?" and get an answer with a path.
- **Free in full, open in full.** No licence server, no seats, no feature gate, no telemetry. Reproducible builds and an SBOM.
- **Remote and fleet.** The original has an iPhone viewer for Pro users and *no* remote monitoring for Linux (a request was moved internal in October 2026). A headless daemon plus a browser console makes a rack of machines one screen.
- **Scriptability.** JSON CLI, HTTP API, Prometheus export, deterministic trace files. Anything an operator wants to alert on is a first-class output, not a screenshot.
- **Extensibility.** Skins as data *and* providers as plugins: a vendor SDK, a container runtime, a NAS, an eGPU enclosure, a Raspberry Pi sense HAT.
- **Reliability as a feature.** Per-provider isolation, deadlines, watchdogs, always-on ring buffer, and a UI that renders gaps rather than freezing. The original's own support answer to stalled graphs is an environment variable that writes a text log.

The one-sentence product thesis:

> **A measuring instrument you can audit**: the same honest, glanceable picture of what your computer is doing that TMOG made famous, open, free, remote-capable and scriptable.

## What we build

Two deliverables, in this order.

1. **The instrument** — a daemon (`vernierd`) with a measuring core, a browser console that becomes the desktop shell, a CLI, and platform providers. Linux first (this environment is Linux), then Windows, then macOS.
2. **The site** — a documentation and download site with the same information architecture as the original's marketing site: downloads with checksums, release notes, per-platform notes, skin authoring guide, privacy statement that can actually be verified against the source.

Reverse-engineering effort is front-loaded into **behaviour, not pixels**: specification first, fixtures second, code third. Visual language is inspired, not copied — different name, our own type, our own marks, our own copy.

## The plan in numbers

| Milestone | Deliverable | Estimate (focused days) |
| --- | --- | ---: |
| M0 | This dossier, spec, architecture, naming shortlist | **done** |
| M1 | Linux core + console: Summary, Performance, Processes, System Info; 6 themes; gaps; CLI JSON | 32 |
| M2 | Actions, Startup apps, Services, Users, Connections, Disk Space | 24 |
| M3 | Recorder/replay, Benchmarks, Installed Apps, Power & Frequency | 20 |
| M4 | Windows and macOS providers behind the same contract; CI on real runners | 40 |
| M5 | Remote view, pairing, fleet, Prometheus/OTLP, provider SDK | 24 |
| M6 | Desktop shells, packaging (AppImage/deb/MSI/DMG/brew/winget), a11y audit, i18n, 1.0 | 20 |

≈ 160 focused days serially (plus a 3-day observation programme); the workstreams are separable, so two people roughly halve the calendar time. Details and acceptance criteria: [07 — Roadmap](07-roadmap.md).

## How we will know it worked

| Test | Pass condition |
| --- | --- |
| Honesty | A fabricated sensor failure produces `unavailable` with a named missing grant, never `0` |
| Gaps | Suspending the machine for 60 s produces a visible gap, not a straight line |
| Correctness | CPU %, memory, disk throughput and network rates agree with `/proc`-derived ground truth within 1 % over a 10-minute golden trace |
| Isolation | A hung provider degrades one tile and is named in the status bar; the rest of the UI keeps sampling |
| Cost | Idle daemon ≤ 60 MB RSS, ≤ 1.5 % of one core at 1 Hz, first frame < 300 ms |
| Portability | The same console binary renders traces recorded on all three platforms |
| Openness | `git clone && npm ci && npm start` yields a working instrument with no account, key or network call |

## The five decisions that need a human

1. **Name** — "Vernier" is the working title; alternatives and trademark checks are in [06](06-differentiators-and-naming.md#5-naming).
2. **Stack** — recommended: TypeScript core + React console + local daemon, with Tauri shells later (rationale and the honest costs in [05](05-architecture.md#2-adr-001--the-stack)). The alternative, a C++/Qt or Rust core, buys native metrics and lower footprint at roughly double the build time and is impossible to compile in this environment.
3. **Scope order** — app first, site later; Linux first, because every page of this dossier can be verified here.
4. **Licence** — Apache-2.0 recommended (patent grant, permissive, business-friendly). MPL-2.0 or GPL-3.0 if copyleft is preferred.
5. **Whether to seek Dave Plummer's blessing** — not required, but a courteous, clearly-disclaimed "inspired by" note and a public commitment not to clone marks or assets costs nothing and protects the project.

## What could kill it

- **Wrong numbers.** A monitor that is subtly wrong is worse than no monitor. Mitigation: fixtures, golden traces, cross-checks against kernel ground truth, and a published methodology.
- **Sensor coverage.** Thermals across AMD/Intel/ARM are a swamp; the original's own answer is "install AMD's SDK and elevate". Mitigation: a provider registry with capability reporting and honest `unavailable` states, not heroics.
- **Trademark drift.** Anything that looks like "TMOG 2" invites a takedown and confuses users. Mitigation: distinct name, no marks in the UI, explicit non-affiliation.
- **Scope.** Twelve destinations is a lot of surface. Mitigation: milestone gates; the MVP is four destinations done honestly.
- **Distribution trust.** System monitors ask for attention and sometimes privilege. Mitigation: signed releases, reproducible builds, no install-time privileges, local-only API by default.

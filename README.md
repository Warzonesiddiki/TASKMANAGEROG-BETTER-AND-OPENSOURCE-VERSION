# Vernier

**An open measuring instrument for your computer.** *Working title — see [naming](docs/06-differentiators-and-naming.md#5-naming).*

A cross-platform system monitor in the spirit of [TMOG (Task Manager OG)](https://tmog.org/) by Dave Plummer: one glance tells you *which process and which subsystem* is spending your computer's time, memory, disk, network and energy — and every number says where it came from or why it is missing.

The difference is that this one is **open source, free in full, scriptable, and built to be extended**.

> **Status: research and planning.** This repository currently holds a reverse-engineering dossier, a product specification, an architecture decision record and a phased plan. No application source yet. See [docs/07-roadmap.md](docs/07-roadmap.md).

---

## Why this exists

TMOG is genuinely good: a shared C++20 measuring core with native Swift/AppKit, Win32 and Qt 6 front ends, twelve destinations, phosphor meters drawn by the app itself, and an unusually honest data model in which *unavailable* is a real answer and a stopped sample leaves a gap instead of a fake line.

It is also closed, partly paywalled ($39.95 for Flight Recorder, Power & Frequency, Connections, Installed Apps, Disk Space, Benchmarks), single-machine, and — by its own public tracker — still fighting freezes, sampling gaps and sensor coverage. 1,548 public reports in twelve weeks describe exactly which parts hurt.

This project keeps the good idea and removes the friction:

| | TMOG | Vernier |
| --- | --- | --- |
| Source | Closed, private | Open (Apache-2.0), reproducible builds |
| Price | Free + $39.95 Pro | Free, all features |
| Platforms | macOS, Windows, Linux (three native UIs) | Same targets, one measuring core + one console UI |
| Remote / headless | iPhone view, Pro, no Linux remote | Local daemon, browser console, read-only pairing, fleet view |
| Scripting | None | Stable JSON CLI, HTTP API, Prometheus exporter |
| Extensibility | Skins are data-only | Skins **and** metric providers are pluggable |
| Diagnostics | Environment-variable sampling log | Built-in recorder, always-on ring buffer, per-provider health |
| Telemetry | No metrics uploaded | No telemetry at all |

## What is *not* happening here

- We are not cracking, patching or unlocking TMOG Pro. There is no licence circumvention in this repository and there will not be.
- We do not ship, mirror or link to Dave Plummer's binaries, artwork, icons, fonts or site copy.
- We are not affiliated with, endorsed by, or named after TMOG. "TMOG" and "Task Manager OG" are his marks; this project uses neither as its name.
- Reverse engineering here is **clean-room behavioural work from public artefacts** — documentation, the public tracker, published formats and black-box observation. See [the method](docs/01-reverse-engineering-method.md).

## The dossier

Read in this order:

| # | Document | What it answers |
| --: | --- | --- |
| 00 | [Executive summary](docs/00-executive-summary.md) | The whole plan on two pages |
| 01 | [Reverse-engineering method](docs/01-reverse-engineering-method.md) | How we take a closed product apart legally and usefully |
| 02 | [Product dossier](docs/02-product-dossier.md) | What TMOG is, feature by feature, with dates and sources |
| 03 | [Product specification](docs/03-product-spec.md) | What we are building, screen by screen |
| 04 | [Metrics and sources](docs/04-metrics-and-sources.md) | Every reading, its unit, its availability rules and where each OS keeps it |
| 05 | [Architecture](docs/05-architecture.md) | Stack choice, data flow, performance budgets, testing |
| 06 | [Differentiators and naming](docs/06-differentiators-and-naming.md) | Why anyone would switch, and what to call it |
| 07 | [Roadmap](docs/07-roadmap.md) | Six milestones, acceptance criteria, estimates |
| 08 | [Risks and legal](docs/08-risks-and-legal.md) | Trademark, clean-room walls, security, privacy |
| 09 | [Evidence log](docs/09-evidence-log.md) | Every claim, its URL, its date and its confidence |
| — | [Issue analysis](docs/research/issues-analysis.md) | What 1,548 public bug reports say (regenerable) |

## Reproducing the research

```bash
python3 research/fetch_issues.py     # pulls the public tracker (needs gh)
python3 research/analyze_issues.py   # regenerates docs/research/issues-analysis.md
```

Raw tracker data is deliberately **not** committed; the scripts and the generated report are.

## Licence

Code: Apache-2.0 (the licence text lands with the first source commit; the decision and its alternatives are in [docs/08](docs/08-risks-and-legal.md#11-governance)). Documents: CC BY 4.0.
"TMOG" and "Task Manager OG" belong to their owner. See [docs/08-risks-and-legal.md](docs/08-risks-and-legal.md).

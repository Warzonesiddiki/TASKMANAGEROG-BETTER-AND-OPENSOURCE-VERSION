# 06 — Positioning, differentiators and naming

## 1. The landscape

| Product | Platform | Open | Free | Strengths | Where it leaves a gap |
| --- | --- | --- | --- | --- | --- |
| **TMOG** | macOS, Windows, Linux | ✗ | Free + $39.95 | Native craft, honest data model, designed instrument, skins | Closed, paywalled depth, no remote/fleet, no scripting, recurring stability reports |
| Mission Center | Linux (+ Windows port) | ✓ (GPL) | ✓ | Good-looking Linux monitor, modern stack | Linux-first, no cross-platform parity, no fleet/API story |
| btop / htop / bottom | Terminal | ✓ | ✓ | Fast, scriptable-ish, beloved | No history replay, no per-OS depth (GPU/SMART/services), not a "product" for a desktop user |
| Glances | Any (Python) | ✓ | ✓ | API + web UI, plugins, cross-platform | Python footprint, inconsistent metric semantics, dated UI, weak per-process depth |
| Netdata | Linux/macOS, servers | ✓ | ✓ (cloud tier) | Real-time, alerting, dashboards | Server/agent mindset, heavy, cloud upsell, not a desktop task manager |
| Windows Task Manager / Activity Monitor | One OS each | ✗ | ✓ | Always there | Historic UX, limited history, no cross-OS model |
| Process Explorer / Sysinternals | Windows | ✗ | ✓ | Deepest Windows process detail | Windows only, no history/replay, expert-only |
| iStat Menus / Stats (macOS) | macOS | partly | $ / free | Menu bar polish, sensors | macOS only, no process-level narrative |
| Prometheus + node_exporter + Grafana | Linux/servers | ✓ | ✓ | Industry standard, long retention | Not a desktop instrument; no per-process story; needs a stack |

**The empty square:** a *cross-platform desktop-quality instrument* that is open, free in full, has per-process depth, records and replays, and can also watch a fleet — without a cloud, an account or a licence. Nobody occupies it. TMOG is close but closed and paid; Glances is open but not an instrument; Netdata is a server tool; the rest are single-OS or terminal-only.

## 2. Who this is for (jobs to be done)

| Persona | The job | What they get here |
| --- | --- | --- |
| **Developer on a laptop** | "My fans spin up when I compile; which cores, which process, is it throttling?" | P/E-core visibility, per-core frequency and temperature, build attribution, energy per process |
| **Ops / homelab** | "Forty boxes, which one is unhappy, and can I alert on it?" | Fleet view, Prometheus export, CLI JSON, recordings I can attach to a ticket |
| **Support engineer** | "A user says it's slow; I need evidence I can trust and share." | Redacted report, `.vntr` recording, provider health, provenance on every number |
| **Privacy-conscious user** | "I want a monitor that isn't also a data pipeline." | No telemetry, no account, local-only default, auditable source |
| **Learner** | "How does an OS actually report CPU time?" | Every metric links to the file or counter it came from |
| **Plugin author** | "My hardware isn't covered." | Provider SDK with a manifest and JSON-RPC, no fork required |

## 3. The five differentiators, stated as claims we can defend

1. **Auditable.** Click any reading and see the metric id, provider, native source, timestamp and state. No other desktop monitor does this. It is a UI feature *and* a cultural one.
2. **Truthful about failure.** `unavailable` is a first-class value with an actionable sentence. The status bar counts gaps. Sleep is a labelled void in the graph, not a straight line.
3. **Free and open, without a crippled tier.** No seats, no licence server, no "Pro" section. Every destination the original gates is in the default build.
4. **Remote and scriptable by design.** The console is an API client, so remote is the same product, and the CLI is a first-class citizen. Prometheus and JSONL make it a monitoring citizen instead of a screenshot generator.
5. **Extensible at both ends.** Skins change the look; providers add sensors. A provider is a small executable with a declared permission set, and the daemon isolates its failures.

**What we do not claim:** "more native than TMOG". It is not, and pretending otherwise would be the first lie in a product about honesty. We claim *more open, more reachable, more scriptable, more diagnosable* — and we say plainly where a native implementation still wins (idle footprint, native table feel).

## 4. Anti-goals

- No "boost", "clean", "optimise" or "free up RAM" buttons. A monitor reports; it does not pretend to heal.
- No cloud account, sync, telemetry, ads or affiliate installers.
- No deleting files from the disk analyser.
- No LLM in the default path. The Advisor is rules first; a model is opt-in and local.
- No Windows-only, Linux-only or macOS-only features without an explicit `unsupported` explanation.
- No copying of TMOG's art, icons, fonts, copy, screenshots or name.
- No forks of the original binary, no licence circumvention, no leaked builds.

## 5. Naming

Criteria, in order: pronounceable in one try; short; not a trademark in the same class (software/system utilities); free npm, PyPI and GitHub org as far as we can check; not a pun that ages badly; survives a logo.

| Candidate | Why it fits | Collision check (2026-10-26) | Verdict |
| --- | --- | --- | --- |
| **Vernier** *(working title)* | A vernier scale reads a measurement more precisely than the main scale — exactly the pitch | npm `vernier` taken, PyPI taken, GitHub org `vernier` likely taken; **Vernier Software & Technology** is a long-standing education-tech brand → trademark risk in software | Good metaphor, risky mark |
| **Ammeter** | Measures current; the product measures what is happening *now*; short, real word | Not yet checked in depth | Strong candidate |
| **Cathode** | The phosphor heritage (VFD/CRT) without borrowing TMOG's look; evokes "the screen that tells you" | npm and PyPI taken (`cathode` 1.0.1); GitHub org likely taken | Nice, crowded |
| **Phosphor** | Direct nod to the meter aesthetic | npm taken, PyPI taken | Crowded |
| **Plumbline** | A tool for finding what is true about a structure; a nod to the author's name without using it | `plumb` is crowded in npm; `plumbline` less so | Charm, but too cute |
| **Tach** | Tachometer; short, punchy; developer-friendly | `tach` is a real Python dependency tool → confusion | Reject |
| **Galvo** | Galvanometer, the moving-needle instrument | Short, unusual, probably free | Good fallback |

**Recommendation.** Keep **Vernier** as the internal working title for this dossier (stable links), but **do not ship it** until a trademark search clears class 9/42. **Ammeter** is the leading alternative: it is the only candidate whose meaning is *literally* the product's job, it is a common noun with no dominant software brand, and `ammeter` reads well in a CLI (`ammeter watch`, `ammeter doctor`).

Naming rules regardless of the choice:

- Never `TMOG`, `Task Manager OG`, `Task Manager` + suffix, or anything a reasonable person would read as the original.
- Package names: `<name>`, `<name>-daemon`, `<name>-console`, npm scope `@<name>/*`.
- The site says "inspired by TMOG" once, plainly, with a link and a non-affiliation sentence — and nowhere else.
- Domain: prefer the tool name without a TLD pun; keep a `docs.` subdomain for the manual.

## 6. Message architecture

**One line:** *An open measuring instrument for your computer — free, auditable, and honest about what it cannot measure.*

**Three proof points:** every reading has a source; gaps are drawn, not smoothed; it runs on everything and talks to everything.

**The comparison page** (site, M6) is a table, not a rant: feature by feature, with the date checked and a link to the source of each claim about the other product. Comparative claims must stay factual and dated; see [08](08-risks-and-legal.md#7-comparative-advertising).

## 7. Go-to-market

1. **Launch where the need is concrete:** r/linux, r/sysadmin, Hacker News "Show HN", Lobsters, the AUR and Flathub communities, Homebrew and winget submissions.
2. **Lead with the recording.** A 60-second clip of a real fan spin-up, recorded at 1 Hz, scrubbed back, with the responsible process named — that is the product in one motion. The original's own Pro pitch is the same motion; ours is free and open.
3. **Docs as marketing.** Publish the provider protocol and the methodology page *before* 1.0. Developers judge monitors by their definitions.
4. **Distribution as a feature.** AppImage, deb, tar.gz, Flatpak, AUR, winget, Scoop, brew, MSI, DMG; checksums and SBOM on every release.
5. **Be decent about the incumbent.** Credit the inspiration; never imply endorsement; never use their marks. The fastest way to lose this project's credibility is to look like a knock-off.

## 8. How success is measured

| Signal | Target by 1.0 |
| --- | --- |
| Time from launch to identifying a culprit in the demo scenario | < 60 s |
| Provider coverage on the three reference machines | ≥ 90 % of catalogued metrics `ok`, the rest explained |
| Gap rate during a 24 h soak | 0 unexplained |
| Crash-free sessions | ≥ 99.5 % |
| Issue first response | < 72 h, automated triage label within 1 h |
| Packaging availability | ≥ 6 channels across 3 OSes |
| Contributors with merged PRs | ≥ 10 |
| Users who never create an account | 100 % (there is no account) |

Stars are not a success metric; they are a distribution accident.

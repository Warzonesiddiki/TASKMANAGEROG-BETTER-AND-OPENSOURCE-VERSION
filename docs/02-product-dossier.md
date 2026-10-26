# 02 — Product dossier: what TMOG is

*Snapshot 2026-10-26, version 1.1.0. Confidence tags: **[A]** first-party published documentation, **[B]** black-box observation, **[C]** third-party static analysis, **[D]** user reports, **[E]** press. Sources and dates: [09 — Evidence log](09-evidence-log.md).*

## 1. Identity

| Field | Value | Source |
| --- | --- | --- |
| Product | **TMOG**, "Task Manager OG" | [A] |
| Author | Dave (David W.) Plummer — wrote the original Windows Task Manager, shipped with Windows NT 4.0 in 1996 | [A][E] |
| Vendor | Plummer's Software LLC | [C] |
| Website | `tmog.org` (Cloudflare-fronted static site); store at `store.tmog.org` | [A] |
| Editions | Free; TMOG Pro, one-time **$39.95**, three activations, any mix of OS | [A] |
| Merchant of record | Lemon Squeezy | [A] |
| Public issue tracker | `PlummersSoftwareLLC/tmog-feedback` — 1,548 reports, 2026-07-31 → 2026-10-26 | [D] |
| Source availability | Closed. A request to open-source it (#1568) is open. The repo URL embedded in the Linux build returns 404; no public source repository was found, which is consistent with a private repository but does not prove one exists. | [D][C] |
| Origin story | Built with an AI coding agent from a ~107-page specification, as a test of whether a modern tool could produce a native Windows-class application | [E] |

## 2. Timeline

| Date | Event |
| --- | --- |
| 2026-07-31 | Public tracker opens; first beta feedback |
| 2026-08-23 | Public announcement on X ("I wrote a new Task Manager that runs natively on Windows, macOS and Linux") |
| 2026-08 → 09 | macOS beta, then Windows/Linux builds; press wave (Engadget, Thurrott, PC Gamer, MajorGeeks, AUR packaging) |
| Late 2026-09 | RTM **1.0.0** on all three platforms; Windows signing, Pro licensing, screensaver |
| 2026-10-06 → 10 | Windows **1.0.1** hotfix (sleep/wake, hang watchdog, Server editions, vendor SDK failures, shadow-copy security flag) |
| **2026-10-26** | **1.1.0** — accessibility, settings, Installed Apps uninstall (Win/Linux), Disk Space history, Drivers page rebuild (Win), Linux Intel GPU/SMART/no-systemd, macOS menu-bar SSD meter, per-platform drawing throttles |

## 3. Architecture as claimed and as observed

**Claimed [A]:** "One shared C++20 measuring core. Three native hosts keep models, actions, serialization, and metric semantics aligned." Swift + AppKit on macOS, C++ + Win32 on Windows, C++ + Qt 6 on Linux. No Electron, no web view, no embedded browser.

**Observed [C]:** the Linux binary links Qt6 Widgets/Gui/Core/Svg/Network/OpenGL/Multimedia, `libsystemd` (D-Bus for `org.freedesktop.systemd1` and `org.freedesktop.login1`), and bundles Qt 6.8.3. A first-party SHA-512 implementation and an Ed25519 *verify-only* implementation are present, consistent with locally verified licence signatures. Bundled fonts: Michroma and Selawik (both OFL). Icons: Microsoft Fluent (MIT).

**What this implies for us:** the three-front-end design buys native fidelity and costs roughly three UI codebases. The shared core is the real asset. We reproduce the *seam* (a platform-neutral measurement contract) and spend the saved effort on one excellent console, remote access and extensibility.

## 4. The information architecture

Twelve destinations [A], in navigation order:

1. **Summary** — the hero page: glanceable gauges, CPU overview, top processes, memory, and mini panels for disk, network, energy, thermals, GPU.
2. **Performance** — per-device detail; CPU can switch between **overall, logical processor and NUMA** views; performance/efficiency cores are colour-coded and distinct.
3. **Processes** — live hierarchy with sorting, filtering, identity-safe selection, and the native verbs (End task, Suspend, Resume, Set priority, Open file location, Go to details).
4. **System Info** — OS, firmware, CPU topology, memory modules, disks, adapters, battery.
5. **Startup apps** — what launches at login and whether to stop it.
6. **Users** — local sessions and what they are running.
7. **Services** — system service control.
8. **Power & Freq** *(Pro)* — package/core power, frequencies, policy.
9. **Connections** *(Pro)* — sockets, owners, what is exposed.
10. **Installed Apps** *(Pro)* — inventory, sizes, uninstall on Windows/Linux (1.1).
11. **Disk Space** *(Pro)* — largest files/folders, scan history (1.1), drill-down.
12. **Benchmarks** *(Pro)* — CPU/disk benchmarks with local history.

Adjacent surfaces: **Settings**, **About**, the **popout** (a small always-on-top readout with skins), a **screensaver** (F12) driven by system load, the **Flight Recorder** (Pro) with `.tmogtrace` files, an **iPhone remote view** (Pro, see §8), and an **AI Advisor** prototype in development builds.

*Ambiguity [D]: several 1.0-era reports mention an "App history" tab. In 1.1 the visible navigation matches the twelve above; treat App history as a sub-surface of Processes/Installed Apps until observed.*

## 5. The measurement philosophy — the part worth copying

The site states ten "facts behind the screen" [A]. Four of them are a data-model specification, and they are the most valuable thing in the product:

1. **"Unsupported means unsupported."** TMOG never shows a zero it did not measure. Zero means the provider measured zero.
2. **"A stopped measurement leaves a gap."** Drawing a smooth line through missing samples is a lie.
3. **"Every reading carries an explicit availability state."** A missing sensor cannot quietly become a plausible-looking value.
4. **"A PID is not enough."** Each process is identified by PID **plus creation identity**, so a recycled number cannot redirect an action.

Two more are engineering posture rather than data model: the app can measure itself (self-monitoring option), and it sends no usage statistics, hardware inventory, process information or identifiers; its only routine request is an update check [A].

Everything in our specification follows from these rules. They are also, usefully, the exact places where the original's users report pain: 160 issue titles mention temperature or a sensor (272 reports mention one anywhere in their text), 134 mention a crash, freeze or hang, and 174 mention a gap, jump or wrong reading [D].

## 6. Feature detail worth knowing

**Themes.** Light, Dark, Green phosphor, Amber phosphor, Blue phosphor, Mono; plus saturation and tint settings (1.1 adds Red and Purple tints) [A]. Meters are app-drawn (VFD-style segmented columns with bloom), not images.

**Popout + skins [A].** A detachable readout with a published JSON skin format:

- A skin is one file (`*.tmogskin` or `*.json`) or a folder ending in `.tmogskin` containing `skin.json` plus images.
- Required: `format: 1`, `id`, `name`; everything else inherits from Default.
- Namespaces: `metrics`, `header`, `surfaces`, `typography`, `ink`, `meters`, `quadrants` (and per-style sub-objects `gauge`, `graph`, `columns`).
- Eight meter channels: `cpu`, `memory`, `gpu`, `thermal`, `disk`, `network`, `power`, `alert`.
- Five meter styles: `bars`, `gauge`, `graph`, `vertical`, `rows`.
- Documented fallback philosophy: unknown names and repeats are dropped, not refused; a deleted skin falls back to Default.
- Built-in skins: Default, Winamp, Windows Media Player, Console, Traces, Windows Task Manager.

This is an *intended extension point*, published so third parties can write against it. Implementing a compatible reader is legitimate interoperability — and a good conformance target for us.

**Flight Recorder (Pro) [A].** Records, saves, scrubs and replays the same seven telemetry panels in one interchangeable `.tmogtrace` format on all three platforms. Byte layout is not published.

**Screensaver [A].** F12 opens a system-load screensaver shared across platforms; Escape returns.

**Accessibility (1.1) [A].** Text size 100–200 %, system high-contrast support, screen-reader and keyboard access to meters, graphs and controls.

**Platform notes.**

- **Linux [A]:** powercap energy counters are root-only since kernel 5.10; TMOG shows "Power access restricted" and documents a group-read udev rule rather than elevating. SMBIOS rows need `/sys/firmware/dmi/tables/DMI`; documented tmpfiles rule. Launching via `sudo`/`pkexec`/`doas` is noticed: the app reads/writes the invoking account's settings and shows a "Running as" row. glibc ≥ 2.35, libstdc++ ≥ 12; `.deb`/`.tar.gz` need system Qt ≥ 6.4, so use the AppImage on Ubuntu 22.04. RHEL 9 rebuilds cannot run it.
- **Windows [A]:** x64 and ARM64; signed and timestamped app, screensaver, installer and uninstaller under "David Plummer". Windows 11 target; hotfix work for Windows Server without the Wireless LAN Service and editions without Media Foundation.
- **macOS [A]:** macOS 14+, Apple silicon and Intel, signed and notarized; a Mac App Store edition exists and deliberately omits the remote view.

**Sensors [A].** AMD on Windows needs AMD's free **Ryzen Master Monitoring SDK** plus administrator rights; otherwise an ACPI thermal zone (a board sensor) may be shown and is labelled as such. Radeon GPU readings come from AMD's driver and need neither. Intel thermals have their own setup page. Unavailable states carry actionable links, not silence.

## 7. Commercial and licensing mechanics

- Pro is unlocked by a key inside the same app; the free install stays [A].
- Activation is a single HTTPS POST with the licence key, purchase email, **salted SHA-256 of a platform identifier** (`IOPlatformUUID`, `MachineGuid`, `/etc/machine-id`) and the computer name; the server compares the email to the Lemon Squeezy purchaser [A].
- The returned **signed entitlement** is stored locally (`license.json` under the platform's standard config directory), verified on the machine, and there is **no periodic check-in**; offline use continues indefinitely [A].
- Deactivation releases the seat server-side [A].
- The free-edition promise: free features people rely on will not deliberately be moved behind Pro [A].

For an open-source project this entire subsystem is deleted, not reimplemented. That is a legitimate simplification: no seats, no activation, no account, no server.

## 8. Remote view and AI Advisor (the newest surfaces)

**Remote view (Pro) [A].** iPhone shows the Summary and Performance pages of a Mac, Windows PC or Linux box. Off until *Allow Remote Connections* is enabled. Data travels **directly over the local network**, or from Mac/Linux over the user's own tailnet — never through vendor servers. Pairing shows a six-character code on both screens to compare, the computer advertises itself only during a three-minute pairing window, everything after pairing is encrypted and authenticated, each phone can be revoked, and the phone is **read-only**. The Summary payload includes machine name/model, OS and app version, CPU/memory/disk/network/graphics/neural/temperature/energy readings, and busiest processes (name, PID, CPU, memory). A one-device Performance payload can include IPv4 address and Wi-Fi SSID; never the MAC address. Linux with multiple interfaces sends a combined reading.

**AI Advisor (prototype) [A].** Opt-in; sends a diagnostic snapshot only when the user presses *Analyze*, after previewing it. Snapshot: selected hardware/system info, process and memory measurements, retained graph history; process names optional. Excludes usernames, file paths, serial numbers, network addresses and raw logs. Current prototype targets a **local-network inference server**; the gateway does not persist snapshots.

These two are the most interesting design material in the product, because they show the author's own direction: *the monitor becomes a service and an explainer*. We take that direction further and in the open — a durable local API, a browser console, read-only pairing by default, and an attribution engine that works without any model at all.

## 9. What the public record shows about weaknesses

From 1,548 reports [D] (full breakdown in [the analysis](research/issues-analysis.md)):

- **58 % bugs / 38 % feature requests**; peak ~258 reports in a single week.
- **Self-reported platform:** Windows ~51 %, macOS ~16 %, explicitly "both macOS and Windows" ~14 %, "all platforms" ~10 %, Linux ~9 %.
- **Temperature/thermals leads the title-level themes** (160 titles, 272 reports mentioning it anywhere), followed by **licence/activation/update** (133), **process-table behaviour** (128), **UI/fonts/i18n** (120) and **disk/storage** (104). GPU readings appear in 82 titles but 329 reports, which is what a "my card shows nothing" complaint looks like.
- The maintainer's triage pattern is to move reports internal and close the public issue, sometimes asking for a sampling log via `TMOG_SAMPLING_LOG` — evidence that stalled sampling is a known, diagnosable class.
- Recurring asks that do not exist yet: remote Linux monitoring (moved internal), per-process network, Vim keybindings, sidebar/reorderable tabs, Flatpak/NixOS packaging, portable Windows build, column management, copyable System Info, VRAM utilisation, multi-GPU control, pause/freeze a view, exportable data.

## 10. Ecosystem around it

- AUR: `tmog-appimage`, `tmog-bin` (upstream release tracking), Scoop request, winget manifests, Homebrew interest [E].
- Prior art: **`mikedesu/evildojo-tmog`** (MIT) — a clean-room Linux rebuild in C++11 + Qt 5 with a zero-dependency `/proc` `/sys` core, eight pages, NVML GPU, six themes, 499 fixture checks, and a published recon/plan. It proves the behavioural-rebuild approach works and sets a quality bar for documentation.
- Press coverage treats TMOG as "the Task Manager sequel"; the hook is the author's history, not the feature list [E].

## 11. Open questions (deliberately unanswered)

1. `.tmogtrace` structure, compression, retention.
2. Exact provider algorithms for "energy impact" and network "decaying peak".
3. Sensor-selection precedence across vendors on Windows and macOS.
4. Whether App history is a destination or a sub-view in 1.1.
5. The AI Advisor snapshot schema and model interface.
6. The Windows/macOS privilege model in the same detail as Linux.
7. How Flight Recorder handles gaps and clock jumps in replay.
8. Whether the Mac App Store edition differs in sampling or entitlements beyond the remote view.

Each becomes a **design decision of ours**, recorded in [03](03-product-spec.md), rather than a hole we pretend to fill by guessing.

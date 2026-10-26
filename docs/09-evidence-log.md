# 09 — Evidence log

Every claim this dossier makes about the original traces to a row here. **Class:** A = first-party published documentation, B = black-box observation (none yet — M0b), C = third-party static analysis, D = user reports, E = press or search snippets. **Confidence** reflects how directly the source supports the claim, not how much we like it.

*All web sources accessed 2026-10-26.*

## Identity and history

| ID | Claim | Source | Class | Conf. |
| --- | --- | --- | --- | --- |
| E-01 | The product is "TMOG", short for Task Manager OG, at `tmog.org` | https://tmog.org/ | A | High |
| E-02 | Author is Dave Plummer, who wrote the original Windows Task Manager over 30 years ago | https://tmog.org/ (front-page attribution block); https://www.thurrott.com/windows/windows-11/341878/ | A, E | High |
| E-03 | Vendor is Plummer's Software LLC | AppImage metadata quoted in https://github.com/mikedesu/evildojo-tmog/blob/master/docs/RECON.md | C | Medium |
| E-04 | Public announcement on X, 2026-08-23 | https://x.com/davepl1968/status/2091562472323056070 (search snippet; X not fetched) | E | Medium |
| E-05 | Built with an AI coding agent from a ~107-page specification | https://www.vladan.fr/tmog-task-manager-the-original-creator-of-windows-task-manager-is-back-with-something-better/ | E | Medium |
| E-06 | Described by press as "vibe coded", shipping on three platforms | https://www.engadget.com/2262039/vibe-coded-modern-task-manager-runs-on-mac-and-linux/ | E | Medium |
| E-07 | RTM 1.0.0 on all platforms late September 2026; Windows-only hotfix 1.0.1 | https://tmog.org/release-notes.html | A | High |
| E-08 | 1.1.0 released 2026-10-26 (UTC) for all three platforms | https://tmog.org/release-notes.html ; download cards on https://tmog.org/ | A | High |

## Architecture and platform

| ID | Claim | Source | Class | Conf. |
| --- | --- | --- | --- | --- |
| E-10 | One shared C++20 core; Swift+AppKit on macOS, C++/Win32 on Windows, C++/Qt 6 on Linux; no Electron or web view | https://tmog.org/ (fact 01) | A | High |
| E-11 | Linux binary links Qt6 Widgets/Gui/Core/Svg/Network/OpenGL/Multimedia and `libsystemd`; bundles Qt 6.8.3; verifies licenses with Ed25519 verify-only code and a first-party SHA-512 | RECON notes, https://github.com/mikedesu/evildojo-tmog/blob/master/docs/RECON.md | C | Medium |
| E-12 | Embedded repo URL `github.com/PlummersSoftwareLLC/TMOG` returns 404; no public source repository found (consistent with private, not proof of it) | Same RECON notes; URL fetched 2026-10-26 | C | Medium |
| E-13 | Linux requires glibc ≥ 2.35, libstdc++ ≥ 12; `.deb`/`.tar.gz` need system Qt ≥ 6.4; RHEL 9 rebuilds cannot run it | https://tmog.org/linux.html | A | High |
| E-14 | Windows targets Windows 11 x64 and ARM64; macOS 14+ on Apple silicon and Intel; signed and notarized | https://tmog.org/ | A | High |
| E-15 | Package set: macOS DMG; Windows EXE installer + zip, x64 and ARM64; Linux AppImage, deb, tar.gz, x64 and arm64 | Download cards, https://tmog.org/ | A | High |
| E-16 | Published SHA-256 for each artefact | Download cards, https://tmog.org/ | A | High |
| E-17 | Linux powercap energy counters are root-only since kernel 5.10; TMOG shows "Power access restricted" and documents a udev group-read rule rather than elevating | https://tmog.org/linux.html | A | High |
| E-18 | SMBIOS memory rows come from `/sys/firmware/dmi/tables/DMI`, root-only; documented tmpfiles rule; Raspberry Pi has no table, so rows are "unsupported" | https://tmog.org/linux.html | A | High |
| E-19 | Launching via sudo/pkexec/doas is detected; settings belong to the invoking account; System Info shows a "Running as" row | https://tmog.org/linux.html | A | High |
| E-20 | AMD on Windows requires AMD's free Ryzen Master Monitoring SDK plus administrator; ACPI thermal zone is shown and labelled when that is the only source; Radeon GPU data needs neither | https://tmog.org/amd-thermals.html | A | High |
| E-21 | Intel processors have a separate thermals setup page | Listed in https://tmog.org/sitemap.xml (page not read for this dossier) | A | Medium |

## Product surface

| ID | Claim | Source | Class | Conf. |
| --- | --- | --- | --- | --- |
| E-30 | Twelve destinations: Summary, Performance, Processes, System Info, Startup apps, Users, Services, Power & Freq, Connections, Installed Apps, Disk Space, Benchmarks | https://tmog.org/ (fact 02) | A | High |
| E-31 | Pro gates Power & Freq, Connections, Installed Apps, Disk Space, Benchmarks and Flight Recorder | https://store.tmog.org/licenses | A | High |
| E-32 | Meter philosophy: distinguish zero from unavailable; gaps instead of smoothing; explicit availability state; no invented values | https://tmog.org/ (facts 03–05) | A | High |
| E-33 | Process identity = PID + creation identity, so a recycled PID cannot redirect an action | https://tmog.org/ (fact 09) | A | High |
| E-34 | Performance/efficiency cores are colour-coded and distinct; CPU views can switch overall / logical processor / NUMA | https://tmog.org/ (facts 05–06) | A | High |
| E-35 | Six themes: Light, Dark, Green, Amber, Blue, Mono; saturation and tint settings; 1.1 adds Red and Purple tints | https://tmog.org/ ; https://tmog.org/release-notes.html | A | High |
| E-36 | Meters are drawn by the native app (VFD style) | https://tmog.org/ ("the phosphor belongs to the product") | A | High |
| E-37 | Flight Recorder records, saves, scrubs and replays seven telemetry panels in one interchangeable `.tmogtrace` format on all three platforms (Pro) | https://tmog.org/ (fact 07) | A | High |
| E-38 | A system-load screensaver opens with F12 and exits with Escape | https://tmog.org/release-notes.html (RTM) | A | High |
| E-39 | 1.1 accessibility: text size 100–200 %, system high contrast, screen reader and keyboard access to meters, graphs and controls | https://tmog.org/release-notes.html | A | High |
| E-40 | 1.1 settings: network rates in bytes or bits, Red/Purple tints, process row highlights off; sort order and selected device persist | https://tmog.org/release-notes.html | A | High |
| E-41 | 1.1 Windows: one disk per physical drive, close to notification area, System Pressure tile, File activity window, rebuilt Drivers page (Pro), smoother graphs | https://tmog.org/release-notes.html | A | High |
| E-42 | 1.1 Linux: Intel GPU readings, Wi-Fi and memory details, SMART health, works without systemd | https://tmog.org/release-notes.html | A | High |
| E-43 | 1.1 macOS: graphs animate while the app is visible but inactive; menu-bar SSD Space meter shows startup disk free space | https://tmog.org/release-notes.html | A | High |
| E-44 | 1.0.1: sleep/wake fix, hang watchdog scope, Windows Server without WLAN service, Media Foundation requirement for recording, vendor SDK failure handling, Admin App History shadow-copy fix | https://tmog.org/release-notes.html | A | High |
| E-45 | Screenshots exist for Summary, Processes, CPU, Memory, Disks, Network, Energy, Thermals and six themes | Screenshot assets listed on https://tmog.org/ | A | High |
| E-46 | Sidebar order in the 1.0-era Linux build, including a "PRO" group | Screenshot published by techbits.cc, retrieved via image search (second-hand) | E | Medium |
| E-47 | An "App history" tab existed in the 1.0 line and is referenced by 1.1-era reports | https://github.com/PlummersSoftwareLLC/tmog-feedback/issues/1594 ; press reviews | D | Medium |

## Skins (published extension format)

| ID | Claim | Source | Class | Conf. |
| --- | --- | --- | --- | --- |
| E-50 | A skin is data, not code: one `.tmogskin`/`.json` file or a folder ending in `.tmogskin` with `skin.json` plus images | https://tmog.org/skins.html | A | High |
| E-51 | Required keys `format: 1`, `id`, `name`; everything else inherits from Default | https://tmog.org/skins.html | A | High |
| E-52 | Token namespaces: `metrics`, `header`, `surfaces`, `typography`, `ink`, `meters`, `quadrants`; documented value grammar and clamping | https://tmog.org/skins.html | A | High |
| E-53 | Eight meter channels (`cpu`, `memory`, `gpu`, `thermal`, `disk`, `network`, `power`, `alert`) and five styles (`bars`, `gauge`, `graph`, `vertical`, `rows`) | https://tmog.org/skins.html | A | High |
| E-54 | Unknown names and repeats are dropped rather than refused; deleted skins fall back to Default | https://tmog.org/skins.html | A | High |
| E-55 | Built-in skins include Winamp and Windows Media Player tributes; example skins ship as Console, Traces, Windows Task Manager | https://tmog.org/skins.html | A | High |

## Commerce, licensing, privacy

| ID | Claim | Source | Class | Conf. |
| --- | --- | --- | --- | --- |
| E-60 | Pro is $39.95 one-time, three computers, any mix of OS; merchant of record is Lemon Squeezy | https://store.tmog.org/licenses | A | High |
| E-61 | Activation sends key, purchase email, salted SHA-256 of a platform identifier (`IOPlatformUUID`, `MachineGuid`, `/etc/machine-id`) and the computer name | https://tmog.org/privacy.html | A | High |
| E-62 | The returned entitlement is signed and verified locally; no periodic check-in; offline use continues | https://tmog.org/privacy.html | A | High |
| E-63 | Entitlement stored at `~/Library/Application Support/TMOG/license.json`, `%LOCALAPPDATA%\TMOG\license.json`, `~/.config/TMOG/Task Manager TMOG/license.json`; unencrypted, signed | https://tmog.org/privacy.html | A | High |
| E-64 | Automatic update-check behaviour differs by platform and sends no version, metrics or identifiers | https://tmog.org/privacy.html | A | High |
| E-65 | Remote view: off by default, direct LAN or user's tailnet, six-character comparison pairing, three-minute advertisement window, encrypted and authenticated, per-phone revocation, read-only | https://tmog.org/privacy.html | A | High |
| E-66 | Remote Summary payload includes machine name/model, OS and app version, CPU/memory/disk/network/graphics/NPU/temperature/energy and busiest processes; Performance payload may include IPv4 and SSID; never MAC | https://tmog.org/privacy.html | A | High |
| E-67 | AI Advisor is a prototype: opt-in, previewed snapshot, local-network inference server, excludes usernames/paths/serials/network addresses/raw logs | https://tmog.org/privacy.html | A | High |
| E-68 | Free-edition scope: Pro may be added, but existing free features will not deliberately be moved behind Pro | https://tmog.org/privacy.html | A | High |
| E-69 | iPhone remote monitoring is Mac-only per the store's footnote (privacy notice describes Mac/Windows/Linux hosts) | https://store.tmog.org/licenses vs https://tmog.org/privacy.html | A | Low–Medium (conflict) |

## Community and evidence of failure modes

| ID | Claim | Source | Class | Conf. |
| --- | --- | --- | --- | --- |
| E-70 | 1,548 public reports, 2026-07-31 → 2026-10-26; 63 open; 58.2 % bug, 37.7 % feature | Generated: `docs/research/issues-analysis.md` from `research/data/tmog-feedback-issues.json` | D | High (reproducible count) |
| E-71 | Self-reported platform: Windows 789, macOS 249, both 211, all platforms 147, Linux 136, unstated 11 | Same | D | High |
| E-72 | Temperature/thermals and GPU readings are the largest title-level themes; crashes/freezes and licence/update problems follow | Same | D | High |
| E-73 | Longest discussions: Linux Pro registration + update failures (#811, 23 comments), Thermals unavailable (#76), temperature sensor selection (#642), Intel Core Ultra thermals (#831) | https://github.com/PlummersSoftwareLLC/tmog-feedback/issues/811 (+ linked) | D | High |
| E-74 | A 1.0.0 user reported 10–45 s freezes with all graphs stopping; maintainer asked for a `TMOG_SAMPLING_LOG` capture | https://github.com/PlummersSoftwareLLC/tmog-feedback/issues/1004 | D | High |
| E-75 | A CPU-utilisation-over-100 % report on Linux whose thread concluded the tools generally stay under 100 % | https://github.com/PlummersSoftwareLLC/tmog-feedback/issues/1109 | D | Medium |
| E-76 | "Waiting for the first native snapshot" never completing on one Windows machine, 1.0.1 | https://github.com/PlummersSoftwareLLC/tmog-feedback/issues/1594 | D | High |
| E-77 | Request to open-source the project is open | https://github.com/PlummersSoftwareLLC/tmog-feedback/issues/1568 | D | High |
| E-78 | Remote Linux monitoring request closed after being moved internal, "no promise of a release date" | https://github.com/PlummersSoftwareLLC/tmog-feedback/issues/1527 | D | High |
| E-79 | 1.1 shipped `Text size`, so the "option to make texts larger" request (#1577) was addressed | https://github.com/PlummersSoftwareLLC/tmog-feedback/issues/1577 + release notes | D | High |

## Packaging ecosystem and prior art

| ID | Claim | Source | Class | Conf. |
| --- | --- | --- | --- | --- |
| E-80 | AUR packages exist: `tmog-appimage` (proprietary licence ref) and a `tmog-bin` release-tracking package | https://aur.archlinux.org/packages/tmog-appimage ; https://github.com/ProfessorZ/tmog-bin | E | High |
| E-81 | A Scoop (Extras) package request exists | https://github.com/ScoopInstaller/Extras/issues/18971 | E | High |
| E-82 | A winget manifest fork exists under the author's account | `davepl/winget-pkgs` exists (manifest path not found at the guessed location) | E | Low |
| E-83 | `mikedesu/evildojo-tmog` is an MIT, Linux-only clean-room rebuild: C++11 + Qt 5, `/proc`+`/sys` core, eight pages, NVML, six themes, 499 fixture checks | https://github.com/mikedesu/evildojo-tmog | E | High |
| E-84 | Its recon notes document the AppImage's embedded licence ("TASK MANAGER TMOG BETA LICENSE"), bundled fonts (Michroma, Selawik) and Fluent icons | https://github.com/mikedesu/evildojo-tmog/blob/master/docs/RECON.md | C | Medium |
| E-85 | Plummer's Software LLC also publishes `tm`, a small C++20 Windows console task manager (December 2025); its relationship to TMOG is not documented | https://github.com/PlummersSoftwareLLC/tm | A | High (existence), Low (relation) |

## Method references (the list that prompted this work)

| ID | Claim | Source | Class | Conf. |
| --- | --- | --- | --- | --- |
| E-90 | "REA" (Reverse Engineer Anything) is an MCP server/CLI that lets coding agents inspect binaries, Electron apps, .NET assemblies, APKs, firmware and websites and explain/rebuild them | https://github.com/AIshihzong/awesome-reverse-engineer-anything (quoting morluto/rea) | E | Medium |
| E-91 | Controlled studies cited by that list found no significant solve-rate gain from REA, at roughly twice the time and cost (rea-lab, 482 runs; leanrea, 36 runs) | Same, "Does REA help?" section | E | Medium |
| E-92 | The list tags each case REA / AI-RE / Rebuild / Claim? and requires evidence and licences for each entry | Same, tag legend and AGENTS.md | E | High |
| E-93 | The list carries an explicit legal warning: reverse engineering is governed by local law, licences and terms of service | Same, front matter | E | High |
| E-94 | A precedent for this class of work: a Claude Slides front-end deobfuscation that became a source-available editor (baocut) | Same, "Most shared" table | E | Medium |
| E-95 | Registry availability for candidate names: `vernier` taken on npm (0.1.2) and PyPI; `ammeter` a 0.0.1 npm stub, free on PyPI and GitHub; `galvo` free on all three; `cathode` 1.0.1, `phosphor` 0.7.1, `plumbline` 10.0.9 all taken on npm | `npm view`, `https://pypi.org/pypi/<name>/json`, `gh api repos/<name>` | Own check | High (registry state on the date) |

## Deliberate uncertainties

| ID | Open question | Why it stays open | How it would be resolved |
| --- | --- | --- | --- |
| U-01 | `.tmogtrace` layout | Not published; reverse-engineering it would breach our own protocol | Only if the vendor publishes it |
| U-02 | Energy-impact normalisation | Not published | We publish our own formula instead |
| U-03 | Network "decaying peak" constants | Described in prose only | Our own definition, documented |
| U-04 | Sensor precedence on Windows/macOS | Needs hardware and observation | M0b experiments 3 and 6 |
| U-05 | Whether App history is a destination in 1.1 | Conflicting sources (E-47) | M0b experiment 1 |
| U-06 | Exact Pro/remote/iPhone platform matrix | The store footnote and the privacy page disagree (E-69) | Re-check both pages at each release |
| U-07 | Trademark status of "TMOG" / "Task Manager OG" | Not searched; out of scope for a desk review | Formal search before naming any product (see 08) |

## How to refresh this log

1. Re-fetch the site pages listed above; note changes in the log with a new date rather than overwriting.
2. Re-run `python3 research/fetch_issues.py` and `python3 research/analyze_issues.py`; diff the generated report.
3. Re-run the M0b observation sheet if a new release lands before the relevant milestone ships.
4. Anything that cannot be re-checked gets a date and an owner, or it is removed from the dossier.

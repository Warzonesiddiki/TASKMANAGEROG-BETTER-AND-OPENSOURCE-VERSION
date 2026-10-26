# 01 — Reverse-engineering method

> The goal is not to recover someone's source. It is to recover the **contract**: what the product promises, what it measures, how it behaves when reality is inconvenient, and where it fails. Code is one way to learn that; here it is neither necessary nor desirable.

## 1. What "reverse engineer" means in this project

We take apart a closed product in order to build an independent, better implementation of the same idea. The artefacts we may legitimately study fall into five classes, in descending order of authority:

| Class | Evidence | Examples | Why it ranks here |
| --- | --- | --- | --- |
| **A** | First-party published documentation | tmog.org pages, release notes, skin-format guide, Linux/AMD/Intel notes, privacy notice, store page, published checksums | The vendor is *telling* us the contract. Highest confidence, zero legal risk. |
| **B** | First-party behaviour, observed black-box | Running a licensed copy: menus, states, cadence, what happens when a sensor disappears, the file a recording produces | Authoritative but partial: it shows one machine, one build, one moment. |
| **C** | Third-party static analysis of a shipped binary | The `evildojo-tmog` recon notes: linked libraries, embedded doc paths, metric-name strings | Useful for *inventory* (what exists), weak for *semantics* (what it means). Treat as a lead, never as proof. |
| **D** | User reports | 1,548 public issues with platform, version, hardware and reproduction steps | Excellent for failure modes and expectations; unreliable for internals. |
| **E** | Press and blogs | Engadget, Thurrott, PC Gamer, vendor write-ups | Good for dates, pricing and independent confirmation; repeats marketing claims. |

Every statement in this dossier carries a class and a date in [09 — Evidence log](09-evidence-log.md). A claim sourced only from C or E is labelled as such and never promoted to a requirement without an A or B confirmation.

## 2. What the public record actually gives us

An unusual amount, because this product documents its own semantics:

- **Information architecture** — twelve destinations, named, with the order they appear in the navigation, from the vendor's own "ten strongest facts" list.
- **Measurement philosophy** — four rules that are effectively a data-model specification:
  1. distinguish zero from unavailable;
  2. leave a gap when sampling stops;
  3. no sensor may silently become a plausible-looking value;
  4. every reading carries an availability state.
- **Platform source knowledge** — the Linux page names the exact kernel interfaces (`/sys/class/powercap/*/energy_uj`, `/sys/firmware/dmi/tables/DMI`), the permission model (group reads via udev/tmpfiles, explicitly *not* root), and the elevated-launch behaviour (settings ownership, `Running as` row). The AMD page names the Ryzen Master Monitoring SDK, the elevation requirement and every user-visible error string's meaning.
- **A published extension format** — the popout skin JSON: required keys, token namespaces (`surfaces`, `ink`, `meters`, `typography`, `metrics`, `header`), value grammar (hex with alpha, gradient arrays, font objects, image fit modes), clamping rules, and the fallback rules ("unknown names and repeats are dropped rather than refused"). This is intended interoperability and is fair game to implement.
- **Packaging and release engineering** — artefact names, SHA-256 sums, target OS floors (macOS 14+, Windows 11, glibc 2.35 / libstdc++ 12), per-platform channel list (AppImage, deb, tar.gz, MSI/EXE, DMG), and the AUR/winget/Scoop third-party packaging that already exists.
- **Commercial model** — one-time $39.95, three activations, feature split, Lemon Squeezy as merchant of record, activation POST contents (licence key, purchase email, salted machine hash, computer name), locally verified signed entitlement, no periodic check-in.
- **Privacy behaviour** — which HTTP requests are made and when (update manifest on launch, app-control document on macOS/Linux), what they do *not* contain, and the opt-in remote view's transport (direct LAN, or tailnet from Mac/Linux, not via vendor servers, six-character compare-to-pair).

## 3. What the public record does **not** give us

Named explicitly, because these are where invention is required rather than discovery:

1. **Pixel-exact layouts, spacing and type sizes.** Screenshots exist in press and on the site; they are copyrighted images. We may look, measure proportions by eye, and design our own system. We may not trace, crop or ship them.
2. **`.tmogtrace` byte layout.** Described as "one interchangeable format" across three platforms. No public specification. We will design our own trace format and offer import only after an actual file is studied (see §5).
3. **Provider algorithms and thresholds.** E.g. how "energy impact" is normalised across platforms, how the network's "decaying peak" is computed, how CPU percentages are attributed on Windows. We must derive our own definitions and publish them.
4. **Sensor coverage per machine.** Which hwmon chips, which PDH counters, which SMC keys. Publicly only the failures are visible.
5. **Flight Recorder UI semantics.** Scrub granularity, retention, compression. Only the marketing description exists.
6. **The Windows/macOS privilege model** as precisely as the Linux one.
7. **The AI Advisor's snapshot schema.** Described in prose in the privacy notice; not published as a format.

Each of these is a **spec decision** in [03](03-product-spec.md), not an unknown to be guessed.

## 4. The clean-room protocol

Two walls, on purpose.

**Wall 1 — artefacts never enter the implementation.** The analyst reads sites, issues, docs, binaries-as-a-licensed-user, and writes **observation sheets**: numbered, dated, testable statements (`OBS-042: when the thermal provider returns no sensors, the Thermals tile shows "Unavailable" and a link to the AMD setup page`). The implementer works from observation sheets and this dossier only. Pull requests that cite a screenshot, a forum post or "how the original does it" are sent back to be restated as a requirement.

**Wall 2 — no assets, copy or marks.** No icons, fonts, sounds, strings beyond short factual quotations, screenshots, site text, or serialised data from the original. Our type stack is our own choice of OFL fonts; our glyphs are drawn for us; our copy is written by us. The words "TMOG" and "Task Manager OG" appear in this repository only in prose about the product, never as our name, package name, domain or UI label.

**What is explicitly out of bounds,** regardless of jurisdiction: circumventing licence checks, patching the binary, redistributing installers, extracting and reusing embedded artwork, or shipping anything that unlocks Pro. Those are not research; they are the thing this project exists as an alternative to.

## 5. The observation programme (what to do when a licensed copy is available)

This environment cannot reach the download host, so the programme below is queued as **M0b**, to run on a workstation with a legitimate copy. Each step produces a committed observation sheet or fixture, not a screenshot dump.

1. **Cold-start census.** Record time to first frame, the states shown while sampling, and the exact wording of every "waiting"/"unavailable" state. These strings become our state machine, restated in our own words.
2. **Cadence map.** With a screen recorder and a fixed workload, measure the update interval of each panel (the vendor claims display-cadence meters up to ~60 Hz and ~1 Hz data). Confirm which are interpolated and which are real samples.
3. **Sensor ablation.** On Linux, run under a mount namespace that hides `/sys/class/hwmon`, then `powercap`, then `/sys/firmware/dmi`; on Windows, disable a GPU; on macOS, run in a VM with no SMC. Record which readings degrade, which disappear, and what the UI says. This is the fastest way to learn the availability state machine — and it is entirely behavioural.
4. **Identity test.** Force PID reuse (a tight fork loop) and verify that process selection and actions follow *creation identity*, not the number. This confirms a design rule that we will implement from the start.
5. **Gap test.** Suspend the machine for 60 s and resume. Observe whether graphs bridge, gap or interpolate. This is the single most important honesty behaviour to match.
6. **Self-cost measurement.** With the self-monitoring option on, record the monitor's own CPU and memory across the twelve destinations. This sets our performance budget from an external reference rather than a guess.
7. **Trace format experiment.** Record a 10-second session with a single changing variable (e.g. one spinning process), then a second with two. Compare sizes and entropy; change one setting at a time. Only if a lawful basis for format study exists, use a hex diff to infer framing — otherwise treat it as unknown and move on. **Never** require compatibility: our trace format is ours.
8. **Skin conformance.** Author minimal skins that exercise each documented token and clamping rule, then verify fallbacks (bad hex, unknown channel, missing file, oversized values <= the documented clamps). The published guide is the spec; the app is the oracle. The result is a conformance suite for *our* skin engine.
9. **Remote-view pairing observation.** With an iPhone on the same LAN, confirm the six-character comparison, the advertisement window, and read-only enforcement. Do not attempt to defeat authentication.
10. **Update and licence endpoints.** Note the request timing and absence of payload (documented in the privacy notice). Do not intercept, replay or modify; the goal is only to confirm the documented behaviour, and the documentation already suffices.

## 6. The parity harness

Reverse engineering without a test is a rumour. Every behaviour we adopt becomes one of four test kinds:

| Test kind | Shape | Example |
| --- | --- | --- |
| **Fixture parse** | A captured text/binary sample → expected structured reading | `/proc/stat` sample → 2.0 % busy, 0.5 % kernel |
| **Semantics** | A state transition → expected availability | sensor removed mid-run → `unavailable`, history keeps a gap |
| **Golden trace** | A recorded 10-minute session → replayed assertions | CPU%, memory, rates within 1 % of recorded ground truth |
| **Conformance** | A published format → accepted/rejected cases | skin files: 12 must load, 9 must fall back exactly as documented |

Fixtures live under `tests/fixtures/<provider>/<case>/` with a `README` naming the machine class that produced them. A fixture with no provenance is a bug.

## 7. Reasoning about what to steal, adapt or refuse

For each behaviour found, ask three questions in order:

1. **Is it a promise to the user?** ("zero means measured zero", "a gap is the truth", "a PID is not enough".) → adopt as a requirement, implement independently.
2. **Is it a consequence of their architecture?** (three native UIs, Qt on Linux, C++20 core, signed local entitlement.) → do not adopt blindly; choose our own means to the same user-visible end.
3. **Is it their commercial packaging?** (Pro gates, seat limits, iPhone viewer.) → refuse, and say why in public.

That filter is how this dossier turns "what TMOG does" into "what Vernier promises", and it is why the specification in [03](03-product-spec.md) can be more precise than any list of features copied from a marketing page.

## 8. Legal posture in one paragraph

Studying a product's public documentation and behaviour to build an independent, compatible-in-spirit implementation is ordinary interoperability work; in several jurisdictions it is explicitly protected, in others it depends on the terms you accepted. We therefore keep to the conservative path: public artefacts, clean-room separation, no asset reuse, no circumvention, no redistribution, no claim of affiliation. Where the line is genuinely unclear — decompiling, format extraction, automated scraping — the answer is **no**, and the cost of that answer is one unknown we design around. The full register is in [08](08-risks-and-legal.md).

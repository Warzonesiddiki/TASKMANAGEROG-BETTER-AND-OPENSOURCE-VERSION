# 08 — Risks, legal posture and governance

> **Not legal advice.** This is an engineering project's risk register. Before shipping a name, a comparison page or a binary, take advice in the jurisdiction you operate from. Where this document says "do not", the answer is not negotiable without a lawyer's written view.

## 1. Posture in one paragraph

We are building an independent, clean-room implementation of an *idea* — a cross-platform system monitor with honest data semantics — from public documentation and observable behaviour. We do not copy code, assets, copy or marks; we do not circumvent licensing; we do not redistribute the original; we do not claim affiliation. The legal risk that remains is small but not zero, and it concentrates in three places: **the name**, **the comparison page**, and **anyone on the team who looks at the original's source**. Each gets a rule below.

## 2. Trademark

**Facts.** "TMOG" and "Task Manager OG" identify Dave Plummer's product. They are used on the site, in installer names, in the Windows publisher identity, and in the AUR/winget packaging. No public record of a registered mark was checked here; assume common-law and possibly registered rights exist.

**Rules.**

1. Our name, package names, binary names, domain, repo name, UI title and window class contain none of: `TMOG`, `Task Manager OG`, `Task Manager`, `Plummer`, or a confusingly similar string.
2. The UI never shows the word TMOG except in a single "Inspired by" line in *About*, alongside "not affiliated".
3. The repo description and site use nominative reference only ("an open alternative to closed, single-machine system monitors; inspired by TMOG"), once, with a link.
4. No logo shape, colour scheme or typeface is borrowed to evoke the original. Different mark, different type, different palette.
5. If the owner asks us to stop using the name in a specific way, we comply immediately and publicly, even if we believe the use is nominative. The cost of compliance is a sentence; the cost of a fight is the project.

**Takedown readiness.** A `TRADEMARK.md` states our policy; a response plan names one maintainer to answer, with a 72-hour SLA, no public argument, and a prepared rename path (packages, domain, UI strings) that can be executed in a day. This is why the name is deliberately not embedded in metric ids or file formats.

## 3. Copyright

**Never in this repository:** any file extracted from the original; any screenshot; any icon, font file, sound, image or string table; any decompiled or disassembled output; any site HTML/CSS/JS; any serialised skin or trace file from the original.

**Allowed:** short factual quotations from public documentation (fair use / fair dealing, attributed and dated); the *names of features* (facts and short phrases are generally not protectable); metric concepts; our own re-expression of behaviour.

**Assets we ship.** Our own SVG glyphs (drawn for the project), fonts under SIL OFL that we choose (not the pair the original bundles), and generated raster art clearly marked as AI-generated where it is. Dependency licences are audited (MIT/Apache-2.0/BSD/ISC allowed by default; copyleft requires an ADR).

**Contributor rule.** Every PR asserts: "I did not consult the original's source, binaries' disassembly, or assets for this change." If someone has, the change is rejected and the knowledge is quarantined: we do not "launder" it through a rewrite in the same area. That is the whole point of a clean room.

## 4. Third-party formats

| Format | Position |
| --- | --- |
| **Popout skin JSON** | The vendor publishes it *for third parties to author skins*. Implementing a reader, and later an importer, is classic interoperability. We will keep it optional, non-normative, and credit the origin of the format. |
| **`.tmogtrace`** | Not published. We do not reverse it. Our `vntr` format is independent; if the vendor ever documents theirs, an importer can be considered. |
| **CLI/API** | The original has none publicly documented; ours is original work. |
| **File names** (`license.json`, skins folder) | Functional names, but we use our own (`entitlements.json` does not exist in our product at all — there are no entitlements). |

## 5. Reverse-engineering law, honestly summarised

Interoperability work has explicit protection in several regimes, and the protection usually assumes **lawful access, necessity, and a narrow purpose**. We deliberately stay inside the safe lane: public documentation and black-box behaviour, no decompilation.

| Jurisdiction | Instrument | What it generally allows | Our position |
| --- | --- | --- | --- |
| **United States** | 17 U.S.C. §1201; case law including *Sega v. Accolade*, *Sony v. Connectix*, *Google v. Oracle* | Intermediate copying for interoperability and study can be fair use; anti-circumvention is separate and strict | No circumvention, no decompilation; observation only |
| **European Union** | Software Directive 2009/24/EC, arts. 5–6 | Observing, studying and testing a program you lawfully use; decompilation for interoperability under conditions | Rely on art. 5 observation only |
| **United Kingdom** | CDPA ss. 50BA–50C | Similar interoperability carve-outs | Same |
| **India** | Copyright Act 1957, s. 52(1)(ab) and related | Certain acts of adaptation/observation for stated purposes; narrower and less tested | Same, and take local advice before shipping |
| **Australia** | Copyright Act 1968, ss. 47D–47F | Reverse engineering for interoperability under conditions | Same |

Because our method never needs the exceptions that permit decompilation, the legal question reduces to: *did we copy expression?* The clean-room protocol and the asset rules exist to make the answer obviously "no".

## 6. End-user licence terms of the original

A user who installs TMOG accepts its EULA. Observing *your own* licensed copy on *your own* machine is the ordinary use the licence contemplates; it does not become redistribution. What we must never do: share the installer, publish extracted files, or use the licence to justify porting code. If the EULA forbids benchmarking or publishing performance data (many do), we do not publish comparative benchmarks — we compare documented features only.

## 7. Comparative advertising

The comparison page is a factual table with a date and a link per row. Rules:

- Only claims we can point to on the vendor's own site or documentation.
- No denigration, no "abandonware", no speculation about the author's motives.
- Say what the original does better. A comparison that admits a weakness is credible; one that doesn't is an advert.
- Re-verify every row on the date printed at the top; remove rows that become stale.
- Jurisdiction: US Lanham Act §43(a), EU 2006/114/EC, India's Consumer Protection Act 2019 all require comparative claims to be truthful and not misleading. "Up to" claims need their basis stated.

## 8. Privacy and data protection

- **No telemetry**, no account, no analytics in the app or the site. The only network request the daemon can make is one the user initiates (update check that opens a browser page, or a paired remote connection).
- Recordings and exports contain process names, paths and possibly usernames. They are **local files the user creates**; the UI states this at export, offers redaction, and never uploads.
- Remote view transmits metrics between devices the user paired. We are not a processor of that data because it never reaches us. This is a stronger position than the original's and should be stated plainly.
- GDPR/DPDP: if we ever add an optional hosted service (e.g. a fleet relay), it needs a DPIA, a DPA, EU/India data-residency decisions — and it must remain optional with a self-hosted alternative.

## 9. Security

A system monitor is a **privileged observer**, which makes it a target.

| Threat | Mitigation |
| --- | --- |
| Malicious process name / cmdline / SSID used for injection or spoofing | Render as text, never as HTML/format strings; length caps; no terminal escapes passed through |
| Malformed `/proc`, `sysfs`, WMI, SMC responses (fuzzing surface) | Strict parsers, bounds checks, fuzz tests in CI, fail to `error` state |
| Local API hijack by another local user or a malicious web page | Token file 0600, `Origin` checks, no wildcard CORS, no GET side effects, CSRF token on actions |
| Malicious provider plugin | Manifest-declared permissions shown before enabling; no elevation inheritance; optional sandbox; signed registry hashes |
| Privileged helper abused as a confused deputy | Narrow verbs, identity revalidation, no arbitrary paths, audit log |
| Supply chain | Pinned lockfile, `--ignore-scripts`, dependency allowlist, SBOM per release, signed tags, reproducible builds |
| Update hijack | Manual updates, signed artefacts, published checksums, no auto-download |
| Remote pairing abuse | SAS confirmation, 3-minute window, pinned keys, read-only default, revocation, rate limits, lockout |

A `SECURITY.md` with a 90-day disclosure window and a PGP key ships with the source. No bug bounty until there is revenue.

## 10. Risk register

| ID | Risk | Likelihood | Impact | Mitigation | Trigger to act |
| --- | --- | --- | --- | --- | --- |
| R1 | Trademark objection to the project name | Medium | High | Name search before launch; distinct mark; renaming playbook | Any written objection |
| R2 | Accusation of copying assets or code | Low | High | Clean-room protocol; contributor attestations; asset provenance log | Any claim; respond with the log |
| R3 | Wrong numbers erode trust | Medium | High | Fixtures, golden traces, cross-checks, published methodology | Any confirmed numeric bug: patch + post-mortem |
| R4 | Footprint objection ("it's a browser") | High | Medium | Tauri shell, TUI, performance budgets, native sidecars | RSS > 120 MB at M1 gate |
| R5 | Sensor coverage disappointment | High | Medium | Provider registry, `denied`/`unsupported` honesty, docs per OS | < 80 % coverage after M2 |
| R6 | Scope creep across 12 destinations | High | Medium | Milestones with gates; MVP is four destinations | Any milestone overrun > 30 % |
| R7 | Single-maintainer bus factor | Medium | High | Docs-first culture, ADRs, contribution guide, two reviewers | No merged external PR in 90 days |
| R8 | Malicious plugin | Low | High | Sandbox, permissions UI, registry hashes | First plugin submission |
| R9 | Legal demand to remove the comparison page | Low | Medium | Factual, dated, sourced claims; fast takedown of any unverifiable row | Any complaint |
| R10 | Upstream goes open source and absorbs the niche | Low | Medium | Compete on remote/API/plugins; offer to contribute providers | Announcement |
| R11 | Dependency licence contamination | Low | Medium | Licence audit in CI; copyleft requires ADR | New dependency |
| R12 | Burnout | Medium | High | Roadmap that ends, honest estimates, no paid promises | Two missed milestones |

## 11. Governance

- **Licence:** Apache-2.0 for code (patent grant, permissive, business-friendly); CC BY 4.0 for documents. Alternative if copyleft is preferred: MPL-2.0 (file-level) or GPL-3.0.
- **Contributions:** DCO sign-off, no CLA; a short `CONTRIBUTING.md` that repeats the clean-room rule in one sentence and links to the observation-sheet template.
- **Code of conduct:** Contributor Covenant; enforcement by two maintainers; no public pile-ons.
- **Decision making:** lazy consensus, an ADR for contract changes, one "benevolent maintainer" tie-break until there are three regular maintainers.
- **Money:** none at first. If donations appear, they fund hardware for provider verification, and the ledger is public. A future hosted fleet service, if it ever exists, must be optional and self-hostable.
- **No vendor capture:** no contributor may make a feature conditional on a hardware vendor's SDK agreement without an ADR and a fallback path.

## 12. The one-sentence test

Before any change ships, ask: *if this appeared on the front page of Hacker News under the headline "open-source TMOG clone accused of X", would we be comfortable explaining our record?* If the answer needs a paragraph of justification, the change is wrong.

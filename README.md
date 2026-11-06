---
title: SZL Sovereign OS
emoji: 🧠
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
license: apache-2.0
short_description: Folded operator-kernel source. Standalone Space retired.
tags:
  - governance
  - receipts
  - honest-by-design
  - szl-holdings
---

# SZL Sovereign OS

> Control before action. Evidence after.

<!-- szl:header v1 -->
<!-- Native identity: szl-brand@4309f6fce89179331b0b3ed8c99494e76c5be256; Orbit v2 icon. -->
<p>
  <a href="https://github.com/szl-holdings">
    <img src="https://raw.githubusercontent.com/szl-holdings/szl-brand/4309f6fce89179331b0b3ed8c99494e76c5be256/kit/logos/orbit-v2/suite/szl-icon-32.svg" alt="SZL Holdings — Orbit v2" width="32" height="32" />
  </a>
</p>

[Product](https://a-11-oy.com) · [Proof](https://a11oy.net) · [GitHub organization](https://github.com/szl-holdings)
<!-- /szl:header -->

Retained source for the SZL operator-kernel hologram. One Python process. Five organs. Five verticals. Eleven category captures.

**Not a rehost.** vLLM, LangGraph, Llama Guard, Mosaic, Lattice, Guidewire, QuantConnect, Zillow, Sigstore, Electricity Maps, and UDS are *cited leaders of a job*. SZL takes the job, not the code.

## What it contains

| Surface | Honesty |
|---|---|
| Five-organ kernel (YACHAY / YUYAY / YAWAR / OTel / Khipu) | SOURCE-IMPLEMENTED, fail-closed |
| Λ uniqueness | Conjecture 1 OPEN |
| Energy | UNAVAILABLE (never a fabricated joule) |
| Signing | STRUCTURAL-ONLY hash, not a signature |
| killinchu actuation | SIMULATED |
| Real estate occupancy | UNAVAILABLE |
| Standalone Hugging Face Space publication | RETIRED — publisher removed; do not recreate from this repository |

GitHub retains this source for provenance and historical reproducibility. Canonical product/runtime authority is [a11oy](https://github.com/szl-holdings/a11oy) and [platform](https://github.com/szl-holdings/platform). The historical Space identity `SZLHOLDINGS/szl-sovereign-os` is retired as a standalone publication target; this repository does not claim that Space is RUNNING or eligible for recreation.

## Verticals represented in this source

- [a11oy](https://github.com/szl-holdings/a11oy) — inference
- [killinchu](https://github.com/szl-holdings/killinchu) — defense (SIMULATED actuation)
- [david-leads](https://github.com/szl-holdings/david-leads) — insurance, public data
- [szl-quant](https://github.com/szl-holdings/szl-quant) — paper-only
- [szl-real-estate](https://github.com/szl-holdings/szl-real-estate) — public PLUTO/ACS, not an MLS

## Install, verify, run

Stdlib only, Python 3.11–3.13 (CI runs all three). `szl-os` is **not on PyPI**:
no tag or release has been cut, and `publish-pypi.yml` only gates release
readiness until one is. Work from a checkout:

```bash
python -m pip install -e '.[test]'    # optional; the suite also runs from a bare checkout
python -m unittest discover -s tests -v
python scripts/health_smoke.py        # liveness + fail-closed /readyz; one unauthenticated read of the HF Space API
python app.py                         # serves 0.0.0.0:7860 (PORT overrides)
```

## Local API

The retained source can still be exercised locally for tests and reproducibility; that does not establish a hosted runtime.

```
GET  /                      front door: index.html, szl-holo-v2.css, szl-holo-v2.js
GET  /healthz               liveness only ("ready": false)
GET  /readyz                fail-closed readiness (below)
GET  /api/selftest
GET  /api/verticals
GET  /api/captures
GET  /api/organs/integrity  ?seed=11
POST /api/organs/integrity  {"seed":11,"zero_heart":false,"tamper_chain":false,...}
POST /api/verticals/run     {"id":"a11oy","signal":"..."}
POST /api/captures/run      {"id":"vllm","signal":"..."}
```

`/api/verticals/run` and `/api/captures/run` also accept `GET ?id=...&signal=...`.

POST bodies must be UTF-8 JSON objects of at most 200,000 bytes. Invalid JSON,
non-object values, and invalid or excessive body lengths return HTTP 400 with
`{"ok":false,"error":"invalid_json_object"}` before any evaluator runs.
An omitted body or `{}` retains the default local behavior.
A `seed` that `int()` cannot read (text, arrays, objects, NaN, infinity) returns
HTTP 400 with `{"ok":false,"error":"invalid_seed"}`, also before the evaluator
runs; an omitted seed means 11.

`/readyz` is HTTP 200 with `"ready": true` only when this process sent
`SZL_SPACE_API_TOKEN` and the Space API (`SZL_SPACE_API_URL`, default the retired
`SZLHOLDINGS/szl-sovereign-os` endpoint) answered 200. A 401 is `BLOCKED`, an
unauthenticated 200 is `BLOCKED` (`SPACE_PUBLICATION_RETIRED`), anything else is
`UNAVAILABLE`, all as HTTP 503. With the standalone Space retired, 503 is the
expected answer. `SZL_SPACE_API_STATUS` is a test override and can never
authorize.

## Proof boundary

- **Shown here, by `tests/` and `scripts/health_smoke.py`:** the kernel blocks on
  the injected faults the suite exercises (zero heart, fabricated joule, WILLAY
  veto) and flags a tampered chain (`chain_ok: false`); malformed HTTP input gets
  a structured 400 before any evaluator runs; `/readyz` stays 503 unless an
  authorized 200 is observed; every `./` asset `index.html` links is served.
- **Not shown:** a hosted runtime (the standalone Space is retired), any
  signature (receipts are a structural hash), Λ uniqueness (Conjecture 1 is
  open), any energy figure (always `UNAVAILABLE`), real actuation (killinchu and
  quant are `SIMULATED`), or the Lean counts in the footer (pinned constants from
  lutar-lean at `c7c0ba17`, not recomputed here).
- **Open on `main`:** under a WILLAY veto most category captures still report
  `decision: ADVISORY` while `anatomy_verdict` is `BLOCKED`; the fix is in
  [draft PR #25](https://github.com/szl-holdings/szl-sovereign-os/pull/25).
  Until it lands, read `anatomy_verdict`.

See [FOLD.md](FOLD.md) for the archive-bound authority boundary.

Doctrine v11 LOCKED · 749/14/163 · kernel `c7c0ba17` · locked-proven 8 · Λ = Conjecture 1 · Apache-2.0

Estate on Hugging Face: models, datasets and Spaces are published under the [SZLHOLDINGS](https://huggingface.co/SZLHOLDINGS) org.

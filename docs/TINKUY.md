# SZL Tinkuy — bounded three-reviewer research preview

**Tinkuy** means *encounter* in Quechua (Peru's Ministry of Education: https://www.gob.pe/tinkuy). This is a Python software supervisor, **not a first AGI model, trained foundation model, or production release**.

## Canonical integration

GitHub source: `szl-holdings/szl-sovereign-os`, using the existing stdlib HTTP operator kernel.

- `GET /tinkuy`: responsive research UI with CSS 3D rings, expressly *illustrative*, not telemetry.
- `GET /api/tinkuy/status`: returns capabilities and **production admission HOLD**.
- `POST /api/tinkuy/round`: disabled by default; loopback-only, exact Host and Origin check, explicit opt-in, one in-flight / one pass, bounded schema/response, replay suppression for 256 process-local round IDs.
- Provider adapters: local CPU-only Ollama Kimi (`kimi-estate-ops:latest`) and Mistral (`ministral-3:3b`); direct 127.0.0.1 only, no proxies/redirects, alias digest observed before/after; no GPU reservation or credentials.
- **GPT-6 is UNAVAILABLE** in this Python worker without a separate authorized API integration. Caller-supplied notes cannot impersonate a reviewer.
- The pure offline research core supports one to ten bounded iterative passes. Missing reviewer identity ends the loop early, rather than reporting ten passes complete.
- All agent proposals remain untrusted data, not instructions. No GitHub/HF/Cloudflare/PyPI writes, training, archiving, shell execution or payment actions are exposed.
- Source repository and SHA supplied by the operator are **DECLARED, NOT VERIFIED**. SHA-256 receipts are content fingerprints, not publisher signatures or a model identity proof. No automatic promotion.

## Existing SZL formulas inspected, not invented

The local public `szl_os/doctrine.py` declares Doctrine v11 LOCKED, eight formula IDs (F1, F4, F7, F11, F12, F18, F19, F22), trust ceiling 0.97, and an OPEN uniqueness conjecture. `szl_os/organs.py` defines weighted geometric mean `wgm(x,w) = exp(sum(w_i log(x_i)))` for positive inputs with weights summing to one, plus deterministic checks A1–A5. Tinkuy reports these references but does **not** declare new proven theorems or AGI. It has no access to private GPT-6/Kimi/Mistral model weights or internal implementation code.

## Operator-only local smoke

```powershell
$env:TINKUY_ALLOW_LOCAL_INFERENCE = "1"
python -c "from szl_os.serve import serve; serve(host='127.0.0.1', port=7860)"
# Open http://127.0.0.1:7860/tinkuy on that workstation.
```

Local calls run sequentially, CPU only, with finite per-provider timeouts. Do not turn on this route on the public HF Space. Before authorized promotion, require signed source/model identities, stable GPT-6 provider integration, full held-out public benchmark suites, real-browser and accessibility passes, staging canary + rollback, human approvals, and independent published-artifact readback. GitHub checks alone cannot certify production or monetization.

## Replay and network threat boundaries

- Exact loopback Host/Origin checks prevent a website pointing DNS to localhost from invoking model requests.
- Process-local round IDs are single-use (maximum 256), **not** persistent signed anti-replay evidence across restarts.
- Unsupported models, missing digest, changed local alias, malformed response, too many passes or body, missing reviewers, and missing signing keys remain **HOLD/UNAVAILABLE**.
- No successful response constitutes a signed publication, verified training run or human-level intelligence evaluation.

**Source test gates:** standard-library unittests, negative cases for forged claims, malformed content, 10+ round requests, spoofed Host/Origin, same-ID replay, concurrency, clean wheel import, HTML/JavaScript parse and existing OS regression suite. An independent post-deploy test is still required if and when release is approved.

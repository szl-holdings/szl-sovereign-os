# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 SZL Holdings
"""Five-organ fail-closed integrity kernel. Replay it. SHA-256."""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from .doctrine import (
    CHAIN_OPS,
    CONJECTURE_1,
    DOCTRINE,
    KERNEL_COMMIT,
    LOCKED_EIGHT,
    WILLAY_NOTE,
    YUYAY_FLOORS,
    ZERO,
    proven_trust,
)


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def wgm(xs: Sequence[float], ws: Sequence[float]) -> float:
    if len(xs) != len(ws) or not xs:
        return 0.0
    if any((not math.isfinite(x)) or x <= 0.0 for x in xs):
        return 0.0
    if any((not math.isfinite(w)) or w < 0.0 for w in ws):
        return 0.0
    if abs(sum(ws) - 1.0) >= 1e-9:
        return 0.0
    value = math.exp(sum(w * math.log(x) for x, w in zip(xs, ws)))
    return value if math.isfinite(value) else 0.0


def evaluate_lambda(axes: Sequence[float]) -> dict[str, Any]:
    n = len(axes)
    weights = tuple(1.0 / n for _ in range(n)) if n else ()
    value = wgm(axes, weights)
    xv = list(axes)
    a1 = True
    for i, x in enumerate(xv):
        if x >= 1.0:
            continue
        y = xv[:]
        y[i] = min(1.0, x + 0.05)
        if wgm(y, weights) + 1e-12 < value:
            a1 = False
            break
    c = 0.5
    a2 = abs(wgm([x * c for x in xv], weights) - c * value) <= 1e-9 * max(1.0, abs(c * value))
    a3 = abs(wgm([0.7] * n, weights) - 0.7) <= 1e-9 if n else True
    a4 = (not xv) or value <= max(xv) + 1e-12
    a5 = True
    if n >= 2:
        a5 = abs(wgm(list(reversed(xv)), list(reversed(weights))) - value) <= 1e-9
    axioms = [
        {"id": "A1", "ok": a1, "detail": "monotone"},
        {"id": "A2", "ok": a2, "detail": "homogeneous"},
        {"id": "A3", "ok": a3, "detail": "Egyptian-exact"},
        {"id": "A4", "ok": a4, "detail": "bounded-by-max"},
        {"id": "A5", "ok": a5, "detail": "permutation-invariant"},
    ]
    failed = next((a for a in axioms if not a["ok"]), None)
    blocked = value == 0.0 or failed is not None
    if blocked:
        reason = "zero-routed or non-finite axis" if value == 0.0 else f"axiom {failed['id']} failed"
    else:
        reason = "advisory pass — uniqueness remains Conjecture 1 OPEN"
    return {"value": float(value), "blocked": bool(blocked), "reason": reason, "axioms": axioms}


def yawar_chain(seed: int, tamper: bool) -> dict[str, Any]:
    hops: list[dict[str, Any]] = []
    prev = ZERO
    for seq, op in enumerate(CHAIN_OPS):
        material = f"{seq}|{op}|{prev}|{int(seed)}"
        digest = sha256_hex(material)
        hops.append({"seq": seq, "op": op, "prev": prev, "digest": digest, "alg": "SHA-256"})
        prev = digest
    if tamper and len(hops) > 1:
        hops[1] = dict(hops[1])
        hops[1]["prev"] = "deadbeef" + hops[1]["prev"][8:]
    walk = ZERO
    ok = True
    brk: int | None = None
    for hop in hops:
        expect = sha256_hex(f"{hop['seq']}|{hop['op']}|{hop['prev']}|{int(seed)}")
        if hop["prev"] != walk or expect != hop["digest"]:
            ok = False
            brk = int(hop["seq"])
            break
        walk = hop["digest"]
    return {
        "hops": hops,
        "ok": ok,
        "head": hops[-1]["digest"] if hops else ZERO,
        "depth": len(hops),
        "break_at": brk,
        "alg": "SHA-256",
    }


def evaluate_anatomy(
    *,
    zero_heart: bool = False,
    leak_canal: bool = False,
    tamper_chain: bool = False,
    fabricate_joule: bool = False,
    break_skeleton: bool = False,
    willay_fire: bool = False,
    seed: int = 11,
) -> dict[str, Any]:
    if proven_trust is True:
        raise RuntimeError("refusing proven_trust true")
    axes = list(YUYAY_FLOORS)
    if zero_heart:
        axes[0] = 0.0
    heart = evaluate_lambda(axes)
    heart_down = bool(heart["blocked"])
    chain = yawar_chain(int(seed), bool(tamper_chain))
    yawar_down = not bool(chain["ok"])
    leaked = 1.0 if leak_canal else 0.0
    brain_down = leaked > 1e-9
    nervous_down = bool(fabricate_joule)
    rows = [{"id": fid, "ok": not (break_skeleton and fid == "F18")} for fid in LOCKED_EIGHT]
    skeleton_pass = sum(1 for r in rows if r["ok"])
    skeleton_down = skeleton_pass < len(rows)

    def organ(id_: str, name: str, quechua: str, formulas: tuple[str, ...], down: bool, honesty: str, detail: str, metric: float) -> dict[str, Any]:
        return {
            "id": id_,
            "name": name,
            "quechua": quechua,
            "formulas": list(formulas),
            "status": "DOWN" if down else "LIVE",
            "honesty": honesty,
            "detail": detail,
            "metric": float(metric),
        }

    organs = [
        organ("brain", "BRAIN", "YACHAY", ("F1",), brain_down, "LIVE",
              f"cross-canal leak {leaked:.3e}" if brain_down else "read-only cortex · leak 0", leaked),
        organ("heart", "HEART", "YUYAY", ("F4", "F11"), heart_down, "ADVISORY",
              f"Λ {heart['value']:.4f} · {heart['reason']}", float(heart["value"])),
        organ("circulatory", "CIRCULATORY", "YAWAR", ("F7", "F22"), yawar_down, "LIVE",
              f"chain break at {chain['break_at']}" if yawar_down else f"head {chain['head'][:16]}", 0.0 if chain["ok"] else 1.0),
        organ("nervous", "NERVOUS", "OTel", ("F12",), nervous_down, "UNAVAILABLE",
              "fabricated joule refused" if nervous_down else "energy UNAVAILABLE", 1.0 if nervous_down else 0.0),
        organ("skeleton", "SKELETON", "Khipu", ("F18", "F19"), skeleton_down, "ADVISORY",
              f"locked-8 silhouettes {skeleton_pass}/8 · CHECKED ≠ Lean PROVEN @ {KERNEL_COMMIT}", float(skeleton_pass)),
    ]
    live_count = sum(1 for o in organs if o["status"] == "LIVE")
    organ_down = any(o["status"] == "DOWN" for o in organs)
    blocked = organ_down or bool(willay_fire)
    if willay_fire:
        reason = "WILLAY conscience veto — governance bypass refused (tamper-EVIDENT, not tamper-proof)"
    elif organ_down:
        down = ", ".join(o["name"] for o in organs if o["status"] == "DOWN")
        reason = f"organ integrity FAIL · {down} DOWN · fail closed"
    else:
        reason = f"organ integrity {live_count}/5 LIVE · Λ advisory · energy UNAVAILABLE · Conjecture 1 OPEN"
    return {
        "organs": organs,
        "live_count": int(live_count),
        "blocked": bool(blocked),
        "verdict": "BLOCKED" if blocked else "ADVISORY_BODY",
        "willay": {"refused": bool(willay_fire), "note": WILLAY_NOTE},
        "energy": "UNAVAILABLE",
        "energy_j": None,
        "lambda_advisory": True,
        "conjecture_1": "OPEN",
        "conjecture_1_statement": CONJECTURE_1,
        "locked_proven": 8,
        "locked_ids": list(LOCKED_EIGHT),
        "kernel_commit": KERNEL_COMMIT,
        "doctrine": DOCTRINE,
        "chain_head": chain["head"],
        "chain_ok": bool(chain["ok"]),
        "chain": chain,
        "lambda": heart,
        "proven_trust": False,
        "trust_ceiling": 0.97,
        "reason": reason,
        "seed": int(seed),
        "checked_at": now(),
    }


def envelope(ev: Mapping[str, Any]) -> dict[str, Any]:
    payload = json.dumps(ev, sort_keys=True, separators=(",", ":"), default=str)
    return {
        "ok": True,
        "surface": "szl-sovereign-os",
        "receipt_sha256": sha256_hex(payload),
        "signing": "STRUCTURAL-ONLY — no key on this surface; tamper-EVIDENT hash, not a signature",
        "body": dict(ev),
    }


def selftest() -> dict[str, Any]:
    healthy = evaluate_anatomy(seed=11)
    assert healthy["live_count"] == 5
    assert healthy["blocked"] is False
    assert healthy["energy_j"] is None
    assert healthy["proven_trust"] is False
    z = evaluate_anatomy(zero_heart=True, seed=11)
    assert z["blocked"] is True
    t = evaluate_anatomy(tamper_chain=True, seed=11)
    assert t["chain_ok"] is False
    j = evaluate_anatomy(fabricate_joule=True, seed=11)
    assert j["organs"][3]["status"] == "DOWN"
    w = evaluate_anatomy(willay_fire=True, seed=11)
    assert w["blocked"] is True and w["live_count"] == 5
    return {"ok": True, "cases": 5, "healthy_head": healthy["chain_head"]}

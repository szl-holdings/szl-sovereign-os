# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 SZL Holdings
"""Five verticals. Each decision walks the organs. No fabricated occupancy, joule, or fill."""
from __future__ import annotations

import re
from typing import Any

from .doctrine import KERNEL_COMMIT, YUYAY_FLOORS, proven_trust
from .organs import envelope, evaluate_anatomy, evaluate_lambda, sha256_hex

VERTICALS = (
    {
        "id": "a11oy",
        "lane": "Inference",
        "github": "https://github.com/szl-holdings/a11oy",
        "space": "https://huggingface.co/spaces/SZLHOLDINGS/a11oy",
        "actuation": "REPORTED",
    },
    {
        "id": "killinchu",
        "lane": "Defense",
        "github": "https://github.com/szl-holdings/killinchu",
        "space": "https://huggingface.co/spaces/SZLHOLDINGS/killinchu",
        "actuation": "SIMULATED",
    },
    {
        "id": "david-leads",
        "lane": "Insurance",
        "github": "https://github.com/szl-holdings/david-leads",
        "space": "https://huggingface.co/spaces/SZLHOLDINGS/david-leads",
        "actuation": "REPORTED",
    },
    {
        "id": "szl-quant",
        "lane": "Finance",
        "github": "https://github.com/szl-holdings/szl-quant",
        "space": "https://huggingface.co/spaces/SZLHOLDINGS/szl-quant-live",
        "actuation": "SIMULATED",
    },
    {
        "id": "real-estate",
        "lane": "Real estate",
        "github": "https://github.com/szl-holdings/szl-real-estate",
        "space": "https://huggingface.co/spaces/SZLHOLDINGS/szl-real-estate",
        "actuation": "ROADMAP",
    },
)


def _willay(signal: str) -> bool:
    return bool(re.search(r"ignore (the )?policy|bypass (the )?gate|disable willay|override lambda|jailbreak", signal, re.I))


def run_vertical(vertical_id: str, signal: str, *, seed: int = 11) -> dict[str, Any]:
    if proven_trust is True:
        raise RuntimeError("refusing proven_trust true")
    meta = next((v for v in VERTICALS if v["id"] == vertical_id), None)
    if meta is None:
        return envelope({"ok": False, "error": "unknown vertical", "id": vertical_id})
    fire = _willay(signal)
    fabricate = bool(re.search(r"fabricate (a )?joule", signal, re.I))
    anatomy = evaluate_anatomy(willay_fire=fire, fabricate_joule=fabricate, seed=seed)
    axes = list(YUYAY_FLOORS)
    lam = evaluate_lambda(axes)
    decision = "BLOCKED" if anatomy["blocked"] else "ADVISORY"
    actuation = "NONE"
    output = anatomy["reason"]

    if not anatomy["blocked"]:
        if vertical_id == "a11oy":
            output = "gated inference · YACHAY read-only · receipt sealed"
            actuation = "NONE"
        elif vertical_id == "killinchu":
            hostile = bool(re.search(r"hostile|weaponized|raid|swarm", signal, re.I))
            inside = bool(re.search(r"geofence|no-fly|restricted|inside", signal, re.I))
            if hostile and inside:
                decision = "ADVISORY"
                actuation = "SIMULATED"
                output = "ROE pass · interdiction SIMULATED · no weapon command"
            else:
                decision = "BLOCKED"
                output = "deny-by-default ROE"
        elif vertical_id == "david-leads":
            if re.search(r"ssn|medical|credit file", signal, re.I):
                decision = "BLOCKED"
                output = "private field refused · public data only"
            else:
                output = "public FEMA/assessor path · 0 private signals"
        elif vertical_id == "szl-quant":
            actuation = "SIMULATED"
            output = "paper-only advisory · not financial advice · a price is not a fill"
        elif vertical_id == "real-estate":
            if re.search(r"\bmls\b|lockbox|occupancy of unit", signal, re.I):
                decision = "BLOCKED"
                output = "MLS/unit occupancy refused · PLUTO is not occupancy"
            else:
                actuation = "ROADMAP"
                output = "public PLUTO/ACS underwriting · unit occupancy UNAVAILABLE · no listing, no close"

    body = {
        "vertical": vertical_id,
        "lane": meta["lane"],
        "signal": signal,
        "decision": decision,
        "output": output,
        "actuation": actuation,
        "lambda": lam["value"],
        "lambda_advisory": True,
        "energy": "UNAVAILABLE",
        "energy_j": None,
        "proven_trust": False,
        "kernel_commit": KERNEL_COMMIT,
        "anatomy": anatomy,
        "github": meta["github"],
        "space": meta["space"],
        "payload_sha256": sha256_hex(signal),
    }
    return envelope(body)

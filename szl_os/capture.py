# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 SZL Holdings
"""Category capture — take the JOB from the leader, never the code.

Each entry names the public leader of a category, the job they own, and the
SZL original that seizes that job under receipts + fail-closed doctrine.
Nothing here imports, wraps, or rehosts a leader's runtime.
"""
from __future__ import annotations

import re
from typing import Any, Callable

from .doctrine import KERNEL_COMMIT, proven_trust
from .organs import envelope, evaluate_anatomy, sha256_hex

# Leaders are CITED, not affiliated. SZL is not Anduril, Defense Unicorns,
# Zillow, vLLM, LangChain, True Anomaly, Guidewire, or Sigstore.


def _willay(signal: str) -> bool:
    return bool(
        re.search(
            r"ignore (the )?policy|bypass (the )?gate|disable willay|override lambda|jailbreak",
            signal,
            re.I,
        )
    )


def _receipt(kind: str, leader: str, ours: str, signal: str, extra: dict[str, Any]) -> dict[str, Any]:
    anatomy = evaluate_anatomy(willay_fire=_willay(signal), seed=11 + (len(signal) % 17))
    blocked = bool(anatomy["blocked"])
    body = {
        "kind": kind,
        "leader_cited": leader,
        "szl_original": ours,
        "not_a_rehost": True,
        "affiliation": "none",
        "signal": signal,
        "decision": "BLOCKED" if blocked else extra.get("decision", "ADVISORY"),
        "reason": anatomy["reason"] if blocked else extra.get("reason", ""),
        "energy": "UNAVAILABLE",
        "energy_j": None,
        "proven_trust": False,
        "kernel_commit": KERNEL_COMMIT,
        **extra,
        "anatomy_verdict": anatomy["verdict"],
        "chain_head": anatomy["chain_head"],
    }
    return envelope(body)


def seize_vllm(signal: str) -> dict[str, Any]:
    """Category: high-throughput inference serve. Leader: vLLM (PagedAttention).
    Ours: schema-outside-weights serve. Not a vLLM/TGI/TRT-LLM copy."""
    schema_ok = "schema" in signal.lower() or "receipt" in signal.lower() or len(signal) > 12
    return _receipt(
        "inference-runtime",
        "vLLM",
        "szl-serve",
        signal,
        {
            "decision": "ADVISORY" if schema_ok else "BLOCKED",
            "reason": "schema sits outside the weights · GPU ROADMAP · energy UNAVAILABLE",
            "tokens_per_sec": None,
            "honesty": "REPORTED",
            "they_own": "paged KV, tokens/sec",
            "we_own": "receipted serve, schema-outside-weights, honest UNAVAILABLE joules",
        },
    )


def seize_langgraph(signal: str) -> dict[str, Any]:
    """Category: agent graphs. Leader: LangGraph. Ours: Ouroboros bounded loop-tax."""
    hops = min(8, max(1, len(signal.split())))
    tax = round(min(0.97, 0.08 * hops), 4)
    return _receipt(
        "agent-graph",
        "LangGraph",
        "ouroboros",
        signal,
        {
            "decision": "ADVISORY",
            "reason": f"bounded recursion · loop-tax {tax} · Bekenstein budget not a theorem",
            "hops": hops,
            "loop_tax": tax,
            "honesty": "MODELED",
            "they_own": "graph state, checkpoints, durable execution",
            "we_own": "fail-closed hop budget, receipt per hop, WILLAY veto",
        },
    )


def seize_guardrails(signal: str) -> dict[str, Any]:
    """Category: LLM refusal. Leader: Llama Guard / NeMo Guardrails.
    Ours: WILLAY inspectable classifiers. Tamper-EVIDENT, not tamper-proof."""
    fire = _willay(signal)
    return _receipt(
        "refusal",
        "Llama Guard / NeMo Guardrails",
        "WILLAY",
        signal,
        {
            "decision": "BLOCKED" if fire else "ADVISORY",
            "reason": "WILLAY conscience veto" if fire else "inspectable classifiers · trust ceiling 0.97",
            "willay_fire": fire,
            "honesty": "REPORTED",
            "they_own": "classifier weights, policy YAML",
            "we_own": "auditable rules, receipted refusal, never hidden",
        },
    )


def seize_mosaic(signal: str) -> dict[str, Any]:
    """Category: space-domain awareness. Leader: True Anomaly Mosaic.
    Ours: khipu-sda-core clean-room residual. Not affiliated."""
    predicted, observed, threshold = 0.41, 0.88, 0.25
    value = abs(observed - predicted)
    return _receipt(
        "sda",
        "True Anomaly Mosaic",
        "khipu-sda-core",
        signal,
        {
            "decision": "ADVISORY",
            "reason": f"MODELED residual {value:.3f} {'TRIP' if value > threshold else 'quiet'} · not a detection ATO",
            "residual": value,
            "trip": value > threshold,
            "honesty": "MODELED",
            "affiliation": "none — inspired by the category, not the product",
            "they_own": "commercial SDA picture",
            "we_own": "Λ-gated residual + signed advisory, SIMULATED actuation",
        },
    )


def seize_lattice(signal: str) -> dict[str, Any]:
    """Category: counter-UAS C2. Leaders: Anduril Lattice, Dedrone.
    Ours: killinchu. Public actuation SIMULATED."""
    hostile = bool(re.search(r"hostile|weaponized|raid|swarm", signal, re.I))
    inside = bool(re.search(r"geofence|no-fly|restricted|inside", signal, re.I))
    roe = hostile and inside
    return _receipt(
        "counter-uas",
        "Anduril Lattice / Dedrone",
        "killinchu",
        signal,
        {
            "decision": "ADVISORY" if roe else "BLOCKED",
            "reason": (
                "ROE pass · HOSTILE+inside · actuation SIMULATED · no weapon command"
                if roe
                else "deny-by-default ROE · CIVIL/UNKNOWN or outside geofence"
            ),
            "actuation": "SIMULATED",
            "roe": roe,
            "honesty": "SIMULATED",
            "they_own": "sensor fusion + effector integration",
            "we_own": "receipt per interdiction, 13-axis Λ, operator-owned effector",
        },
    )


def seize_guidewire(signal: str) -> dict[str, Any]:
    """Category: insurance decisioning. Leaders: Guidewire, Verisk.
    Ours: David Leads, public data only."""
    private = bool(re.search(r"ssn|medical|credit file|private claim", signal, re.I))
    return _receipt(
        "insurance",
        "Guidewire / Verisk",
        "david-leads",
        signal,
        {
            "decision": "BLOCKED" if private else "ADVISORY",
            "reason": "private field refused" if private else "public FEMA/assessor only · 0 private signals",
            "honesty": "REPORTED",
            "they_own": "policy admin + catastrophe models",
            "we_own": "public-data lead with a replayable receipt",
        },
    )


def seize_quantconnect(signal: str) -> dict[str, Any]:
    """Category: quant research. Leaders: QuantConnect, OpenBB.
    Ours: szl-quant paper-only. Not financial advice."""
    return _receipt(
        "quant",
        "QuantConnect / OpenBB",
        "szl-quant",
        signal,
        {
            "decision": "ADVISORY",
            "reason": "paper-only · a price is not a fill · not financial advice",
            "actuation": "SIMULATED",
            "honesty": "MODELED",
            "they_own": "backtest + brokerage adapters",
            "we_own": "DSSE-signed advisory, no order routing",
        },
    )


def seize_zillow(signal: str) -> dict[str, Any]:
    """Category: property intelligence. Leaders: Zillow, CoStar, HouseCanary.
    Ours: public-records underwriting. PLUTO != MLS. Occupancy UNAVAILABLE."""
    mls = bool(re.search(r"\bmls\b|lockbox|showing|list the house", signal, re.I))
    return _receipt(
        "real-estate",
        "Zillow / CoStar / HouseCanary",
        "szl-real-estate",
        signal,
        {
            "decision": "BLOCKED" if mls else "ADVISORY",
            "reason": (
                "MLS/lockbox refused — no listing, no close"
                if mls
                else "public PLUTO/ACS underwriting · unit occupancy UNAVAILABLE · not an MLS"
            ),
            "occupancy": "UNAVAILABLE",
            "actuation": "ROADMAP",
            "honesty": "MODELED",
            "they_own": "listings, Zestimate, comps network",
            "we_own": "assessor + FEMA + tract ACS RATE, receipted, no fabricated occupancy",
        },
    )


def seize_sigstore(signal: str) -> dict[str, Any]:
    """Category: supply-chain signatures. Leader: Sigstore / in-toto / SLSA.
    Ours: szl-receipt. This surface is STRUCTURAL-ONLY (no key)."""
    return _receipt(
        "provenance",
        "Sigstore / in-toto / SLSA",
        "szl-receipt",
        signal,
        {
            "decision": "ADVISORY",
            "reason": "STRUCTURAL-ONLY hash · compatible with DSSE, not a fabricated signature",
            "signing": "STRUCTURAL-ONLY",
            "honesty": "STRUCTURAL-ONLY",
            "slsa": "L1 honest · L2 roadmap",
            "they_own": "keyless identity, Rekor, builders",
            "we_own": "governed decision receipt + fail-closed UNSIGNED honesty",
        },
    )


def seize_energy(signal: str) -> dict[str, Any]:
    """Category: energy attestation. Leaders: Electricity Maps, NVIDIA NVML.
    Ours: szl-energy-attest. Never a fabricated joule."""
    fabricate = bool(re.search(r"fabricate (a )?joule|invent watts", signal, re.I))
    anatomy = evaluate_anatomy(fabricate_joule=fabricate, seed=11)
    extra = {
        "decision": "BLOCKED" if anatomy["blocked"] else "ADVISORY",
        "reason": anatomy["reason"] if anatomy["blocked"] else "joules null · honesty UNAVAILABLE until NVML MEASURED",
        "energy": "UNAVAILABLE",
        "energy_j": None,
        "honesty": "UNAVAILABLE",
        "they_own": "grid carbon intensity, GPU power draw",
        "we_own": "MEASURED-or-null receipts, never a painted watt",
    }
    return _receipt("energy", "Electricity Maps / NVIDIA NVML", "szl-energy-attest", signal, extra)


def seize_uds(signal: str) -> dict[str, Any]:
    """Category: airgap deploy. Leader: Defense Unicorns UDS.
    Ours: szl-mesh overlay. Not affiliated. No production ATO claimed."""
    return _receipt(
        "airgap",
        "Defense Unicorns UDS",
        "szl-mesh / szl-fleet-overlay",
        signal,
        {
            "decision": "ADVISORY",
            "reason": "UDS referenced as a category · SZL not affiliated · no production ATO",
            "honesty": "REPORTED",
            "affiliation": "none — USPTO Serial 99831122 cited, not owned",
            "they_own": "UDS Core, Zarf, Pepr",
            "we_own": "doctrine-pinned DSSE overlay on the mesh",
        },
    )


RUNNERS: dict[str, Callable[[str], dict[str, Any]]] = {
    "vllm": seize_vllm,
    "langgraph": seize_langgraph,
    "guardrails": seize_guardrails,
    "mosaic": seize_mosaic,
    "lattice": seize_lattice,
    "guidewire": seize_guidewire,
    "quantconnect": seize_quantconnect,
    "zillow": seize_zillow,
    "sigstore": seize_sigstore,
    "energy": seize_energy,
    "uds": seize_uds,
}

CAPTURES = [
    {
        "id": key,
        "leader": fn.__doc__.split("Leader:")[1].split(".")[0].strip() if fn.__doc__ and "Leader:" in fn.__doc__ else key,
        "ours": fn.__name__.replace("seize_", "szl-"),
        "doc": (fn.__doc__ or "").split("\n")[0],
    }
    for key, fn in RUNNERS.items()
]


def run_capture(leader_id: str, signal: str) -> dict[str, Any]:
    if proven_trust is True:
        raise RuntimeError("refusing proven_trust true")
    fn = RUNNERS.get(leader_id)
    if fn is None:
        return envelope({"ok": False, "error": "unknown capture", "id": leader_id, "known": list(RUNNERS)})
    return fn(signal)

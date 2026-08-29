# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 SZL Holdings
"""SZL Sovereign OS — fail-closed operator kernel.

Stdlib only. SHA-256. Energy UNAVAILABLE. Λ = Conjecture 1 OPEN.
Not a rehost of vLLM, LangGraph, Guardrails, Mosaic, Zillow, or Sigstore.
"""

from .capture import CAPTURES, run_capture
from .doctrine import DOCTRINE, KERNEL_COMMIT, LOCKED_EIGHT, proven_trust
from .organs import evaluate_anatomy, evaluate_lambda, selftest as organ_selftest
from .verticals import VERTICALS, run_vertical

__all__ = [
    "CAPTURES",
    "DOCTRINE",
    "KERNEL_COMMIT",
    "LOCKED_EIGHT",
    "VERTICALS",
    "evaluate_anatomy",
    "evaluate_lambda",
    "organ_selftest",
    "proven_trust",
    "run_capture",
    "run_vertical",
]
__version__ = "0.1.0"

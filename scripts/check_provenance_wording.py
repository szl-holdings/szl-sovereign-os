#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fail if the quant capture claims a DSSE signature this tree does not produce."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from szl_os.capture import run_capture  # noqa: E402


def main() -> int:
    owned = run_capture("quantconnect", "paper check")["body"]["we_own"]
    if "DSSE-signed" in owned:
        print("provenance wording failed: quant capture still says DSSE-signed", file=sys.stderr)
        return 1
    if "structural-only, unsigned" not in owned:
        print("provenance wording failed: quant capture is not structural-only, unsigned", file=sys.stderr)
        return 1
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    image = "mirror.gcr.io/library/python:3.12-slim"
    if image not in dockerfile or image not in requirements:
        print("provenance wording failed: Dockerfile and requirements.txt must both name " + image, file=sys.stderr)
        return 1
    source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "szl_os").glob("*.py"))
    if "sign_receipt" in source or "import szl_receipt" in source:
        print("provenance wording failed: a signer is present without a separate DSSE readback", file=sys.stderr)
        return 1
    print("provenance wording ok: structural-only, unsigned; image python:3.12-slim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

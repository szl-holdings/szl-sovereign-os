#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 SZL Holdings
"""Stdlib HTTP operator kernel. Port 7860. No fabricated joule or signature."""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import __version__
from .capture import CAPTURES, RUNNERS, run_capture
from .doctrine import DOCTRINE, KERNEL_COMMIT, proven_trust
from .organs import evaluate_anatomy, selftest
from .verticals import VERTICALS, run_vertical

ROOT = Path(__file__).resolve().parent.parent


def _json(obj: object) -> bytes:
    return json.dumps(obj, indent=2, default=str).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = f"szl-sovereign-os/{__version__}"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "content-type")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _send(self, status: int, raw: bytes, ctype: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self._cors()
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(max(0, min(length, 200000))) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)
        if path in {"/healthz", "/readyz"}:
            self._send(
                200,
                _json(
                    {
                        "ok": True,
                        "surface": "szl-sovereign-os",
                        "doctrine": DOCTRINE,
                        "kernel_commit": KERNEL_COMMIT,
                        "proven_trust": False,
                        "energy": "UNAVAILABLE",
                        "energy_j": None,
                        "lambda": "Conjecture 1 OPEN",
                        "signing": "STRUCTURAL-ONLY",
                        "hf_push": "ROADMAP",
                        "version": __version__,
                    }
                ),
                "application/json",
            )
            return
        if path == "/api/selftest":
            self._send(200, _json(selftest()), "application/json")
            return
        if path == "/api/verticals":
            self._send(200, _json({"ok": True, "verticals": list(VERTICALS)}), "application/json")
            return
        if path == "/api/captures":
            self._send(
                200,
                _json({"ok": True, "captures": list(CAPTURES), "ids": list(RUNNERS)}),
                "application/json",
            )
            return
        if path == "/api/organs/integrity":
            rec = evaluate_anatomy(seed=int(qs.get("seed", ["11"])[0] or 11))
            self._send(200, _json(rec), "application/json")
            return
        if path == "/api/verticals/run":
            rec = run_vertical(qs.get("id", ["a11oy"])[0], qs.get("signal", [""])[0])
            self._send(200, _json(rec), "application/json")
            return
        if path == "/api/captures/run":
            rec = run_capture(qs.get("id", ["vllm"])[0], qs.get("signal", [""])[0])
            self._send(200, _json(rec), "application/json")
            return
        if path in {"/", "/index.html"}:
            html = (ROOT / "index.html").read_text(encoding="utf-8")
            self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
            return
        self._send(404, _json({"ok": False, "error": "not found"}), "application/json")

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/") or "/"
        data = self._read_json()
        if path == "/api/organs/integrity":
            rec = evaluate_anatomy(
                zero_heart=bool(data.get("zero_heart")),
                leak_canal=bool(data.get("leak_canal")),
                tamper_chain=bool(data.get("tamper_chain")),
                fabricate_joule=bool(data.get("fabricate_joule")),
                break_skeleton=bool(data.get("break_skeleton")),
                willay_fire=bool(data.get("willay_fire")),
                seed=int(data.get("seed") or 11),
            )
            self._send(200, _json(rec), "application/json")
            return
        if path == "/api/verticals/run":
            rec = run_vertical(str(data.get("id") or "a11oy"), str(data.get("signal") or ""))
            self._send(200, _json(rec), "application/json")
            return
        if path == "/api/captures/run":
            rec = run_capture(str(data.get("id") or "vllm"), str(data.get("signal") or ""))
            self._send(200, _json(rec), "application/json")
            return
        self._send(404, _json({"ok": False, "error": "not found"}), "application/json")


def serve(host: str = "0.0.0.0", port: int = 7860) -> None:
    if proven_trust is True:
        raise RuntimeError("refusing proven_trust true")
    port = int(os.environ.get("PORT") or port)
    print(
        f"[szl-sovereign-os] {host}:{port} · energy UNAVAILABLE · Λ = Conjecture 1 · HF push ROADMAP",
        file=sys.stderr,
    )
    ThreadingHTTPServer((host, port), Handler).serve_forever()

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Local liveness smoke, fail-closed 401 readiness, and authorized readback."""
from __future__ import annotations

import json
import os
import secrets
import sys
import threading
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from szl_os.serve import (  # noqa: E402
    Handler,
    ThreadingHTTPServer,
    fetch_space_status,
    readiness_from_space_status,
)


def _get(port: int, path: str) -> tuple[int, dict]:
    connection = HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        body = json.loads(response.read().decode("utf-8"))
        return response.status, body
    finally:
        connection.close()


class _SpaceStub(BaseHTTPRequestHandler):
    accept = ""

    def do_GET(self):  # noqa: N802
        presented = self.headers.get("Authorization", "")
        code = 200 if self.accept and presented == "Bearer " + self.accept else 401
        body = b"{}"
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return


def _authorized_readback(kernel_port: int) -> int:
    """ready=true only when the local authorized endpoint returns 200."""
    token = secrets.token_hex(16)
    _SpaceStub.accept = token
    stub = ThreadingHTTPServer(("127.0.0.1", 0), _SpaceStub)
    stub_port = int(stub.server_address[1])
    thread = threading.Thread(target=stub.serve_forever, daemon=True)
    thread.start()
    saved = {
        name: os.environ.get(name)
        for name in ("SZL_SPACE_API_STATUS", "SZL_SPACE_API_URL", "SZL_SPACE_API_TOKEN")
    }
    try:
        os.environ.pop("SZL_SPACE_API_STATUS", None)
        os.environ["SZL_SPACE_API_URL"] = f"http://127.0.0.1:{stub_port}/"
        os.environ.pop("SZL_SPACE_API_TOKEN", None)
        denied_status, denied = _get(kernel_port, "/readyz")
        if denied_status != 503 or denied.get("ready") is not False or denied.get("reason") != "SPACE_API_UNAUTHORIZED":
            print("health smoke failed: unauthenticated stub was not fail-closed", denied_status, denied, file=sys.stderr)
            return 1
        os.environ["SZL_SPACE_API_TOKEN"] = token
        allowed_status, allowed = _get(kernel_port, "/readyz")
        if allowed_status != 200 or allowed.get("ready") is not True or allowed.get("reason") != "SPACE_API_AUTHORIZED":
            print("health smoke failed: authorized stub success was not ready", allowed_status, allowed, file=sys.stderr)
            return 1
        if allowed.get("space_api") != 200 or token in json.dumps(allowed):
            print("health smoke failed: authorized readback leaked or mislabeled", file=sys.stderr)
            return 1
        os.environ["SZL_SPACE_API_TOKEN"] = secrets.token_hex(16)
        rejected_status, rejected = _get(kernel_port, "/readyz")
        if rejected_status != 503 or rejected.get("ready") is not False or rejected.get("reason") != "SPACE_API_UNAUTHORIZED":
            print("health smoke failed: rejected token was not fail-closed", rejected_status, rejected, file=sys.stderr)
            return 1
    finally:
        for name, value in saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        stub.shutdown()
    print("authorized readback ok")
    return 0


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = int(server.server_address[1])
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    prior = os.environ.get("SZL_SPACE_API_STATUS")
    try:
        status, health = _get(port, "/healthz")
        if status != 200 or health.get("ok") is not True or health.get("check") != "liveness":
            print("health smoke failed: liveness", status, health, file=sys.stderr)
            return 1
        os.environ["SZL_SPACE_API_STATUS"] = "401"
        ready_status, ready = _get(port, "/readyz")
        if ready_status != 503 or ready.get("ready") is not False or ready.get("reason") != "SPACE_API_UNAUTHORIZED":
            print("health smoke failed: 401 was not fail-closed", ready_status, ready, file=sys.stderr)
            return 1
        if ready.get("status") != "BLOCKED" or ready.get("space_api") != 401:
            print("health smoke failed: 401 status label", ready, file=sys.stderr)
            return 1
        os.environ.pop("SZL_SPACE_API_STATUS", None)
        if _authorized_readback(port) != 0:
            return 1
    finally:
        if prior is None:
            os.environ.pop("SZL_SPACE_API_STATUS", None)
        else:
            os.environ["SZL_SPACE_API_STATUS"] = prior
        server.shutdown()
    os.environ.pop("SZL_SPACE_API_TOKEN", None)
    os.environ.pop("SZL_SPACE_API_URL", None)
    live_status, live_auth = fetch_space_status()
    decision = readiness_from_space_status(live_status, live_auth)
    print(
        f"live space_api={live_status} authenticated={live_auth} "
        f"ready={decision['ready']} status={decision['status']} reason={decision['reason']}"
    )
    if live_auth:
        print("health smoke failed: live probe sent authorization", file=sys.stderr)
        return 1
    if decision["ready"] is not False:
        print("health smoke failed: live probe was treated as ready", file=sys.stderr)
        return 1
    if live_status == 401 and decision["reason"] != "SPACE_API_UNAUTHORIZED":
        print("health smoke failed: live 401 was not unauthorized", file=sys.stderr)
        return 1
    print("health smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

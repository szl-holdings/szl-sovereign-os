#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Local liveness smoke, plus fail-closed readiness when the Space API is 401."""
from __future__ import annotations

import json
import os
import sys
import threading
from http.client import HTTPConnection
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
    finally:
        if prior is None:
            os.environ.pop("SZL_SPACE_API_STATUS", None)
        else:
            os.environ["SZL_SPACE_API_STATUS"] = prior
        server.shutdown()
    live = fetch_space_status()
    decision = readiness_from_space_status(live)
    print(f"live space_api={live} ready={decision['ready']} status={decision['status']} reason={decision['reason']}")
    if decision["ready"] is not False:
        print("health smoke failed: live probe was treated as ready", file=sys.stderr)
        return 1
    if live == 401 and decision["reason"] != "SPACE_API_UNAUTHORIZED":
        print("health smoke failed: live 401 was not unauthorized", file=sys.stderr)
        return 1
    print("health smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

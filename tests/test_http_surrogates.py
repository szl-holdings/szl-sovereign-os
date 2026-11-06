# SPDX-License-Identifier: Apache-2.0
"""A JSON string with an unpaired surrogate is invalid input, never a dropped connection."""
import http.client
import json
import threading
import unittest
from contextlib import ExitStack
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from szl_os.serve import Handler

INVALID_JSON = {"ok": False, "error": "invalid_json_object"}
LONE_HIGH = chr(0xD800)
LONE_LOW = chr(0xDFFF)
ASTRAL = chr(0x1F600)  # outside the BMP: json.dumps writes it as a paired escape


def body(obj) -> bytes:
    """Encode the way a JSON client does: ensure_ascii escapes every surrogate."""
    return json.dumps(obj).encode("ascii")


class QuietHandler(Handler):
    def log_message(self, *_args):
        pass


class LoneSurrogates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def post(self, path, raw):
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        try:
            connection.request("POST", path, body=raw, headers={"Content-Type": "application/json"})
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_fixture_bodies_are_ascii_and_decode_to_lone_surrogates(self):
        raw = body({"signal": LONE_HIGH})
        self.assertTrue(raw.isascii())
        self.assertEqual(json.loads(raw)["signal"], LONE_HIGH)

    def test_lone_surrogates_are_rejected_before_any_evaluator_runs(self):
        cases = {
            "/api/verticals/run": ({"id": "a11oy", "signal": LONE_HIGH}, {"id": "killinchu", "signal": "x" + LONE_LOW}),
            "/api/captures/run": ({"id": "vllm", "signal": LONE_HIGH}, {"id": LONE_LOW}),
            "/api/organs/integrity": ({"zero_heart": LONE_HIGH}, {LONE_HIGH: 1}),
        }
        with ExitStack() as stack:
            evaluators = [
                stack.enter_context(patch("szl_os.serve." + name, return_value={"status": "UNEXPECTED_EVALUATION"}))
                for name in ("evaluate_anatomy", "run_vertical", "run_capture")
            ]
            for path, objects in cases.items():
                for obj in objects:
                    with self.subTest(path=path, body=ascii(obj)):
                        self.assertEqual(self.post(path, body(obj)), (400, INVALID_JSON))
            for evaluator in evaluators:
                evaluator.assert_not_called()

    def test_vertical_with_a_lone_surrogate_gets_a_response(self):
        # Unpatched: run_vertical hashed the signal, raised UnicodeEncodeError
        # after the evaluators ran, and the client saw RemoteDisconnected.
        raw = body({"id": "a11oy", "signal": LONE_HIGH})
        self.assertEqual(self.post("/api/verticals/run", raw), (400, INVALID_JSON))

    def test_paired_surrogates_are_ordinary_text(self):
        raw = body({"id": "a11oy", "signal": "route " + ASTRAL})
        self.assertTrue(raw.isascii())
        status, result = self.post("/api/verticals/run", raw)
        self.assertEqual(status, 200)
        self.assertEqual(result["body"]["signal"], "route " + ASTRAL)
        self.assertEqual(result["body"]["decision"], "ADVISORY")


if __name__ == "__main__":
    unittest.main()

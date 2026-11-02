# SPDX-License-Identifier: Apache-2.0
"""HTTP parsing must reject invalid inputs before evaluating a default action."""
import http.client
import json
import threading
import unittest
from contextlib import ExitStack
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from szl_os.serve import Handler


class QuietHandler(Handler):
    def log_message(self, *_args):
        pass


class PostJson(unittest.TestCase):
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

    def post(self, path, body, headers=None):
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        try:
            connection.request("POST", path, body=body,
                               headers=headers or {"Content-Type": "application/json"})
            response = connection.getresponse()
            return response.status, response.getheader("Content-Type"), json.loads(response.read())
        finally:
            connection.close()

    def test_invalid_json_is_rejected_before_any_evaluator_runs(self):
        bodies = (b"{", b" ", b"[]", b"null", b'"text"', b"true", b"42", b"\xff")
        paths = ("/api/organs/integrity", "/api/verticals/run", "/api/captures/run")
        with ExitStack() as stack:
            evaluators = [stack.enter_context(patch("szl_os.serve." + name,
                          return_value={"status": "UNEXPECTED_EVALUATION"}))
                          for name in ("evaluate_anatomy", "run_vertical", "run_capture")]
            for path in paths:
                for body in bodies:
                    with self.subTest(path=path, body=body):
                        status, content_type, result = self.post(path, body)
                        self.assertEqual(status, 400)
                        self.assertEqual(content_type, "application/json")
                        self.assertEqual(result, {"ok": False, "error": "invalid_json_object"})
            for evaluator in evaluators:
                evaluator.assert_not_called()

    def test_invalid_content_lengths_are_structured_errors(self):
        for length in ("invalid", "-1"):
            with self.subTest(length=length):
                status, _, result = self.post("/api/organs/integrity", b"{}",
                                              {"Content-Length": length})
                self.assertEqual(status, 400)
                self.assertFalse(result["ok"])

    def test_oversized_body_is_not_accepted_as_a_valid_truncated_prefix(self):
        # The former 200000-byte read accepted this prefix and ignored the x.
        body = b"{}" + b" " * 199998 + b"x"
        status, _, result = self.post("/api/organs/integrity", body)
        self.assertEqual(status, 400)
        self.assertEqual(result["error"], "invalid_json_object")

    def test_empty_object_and_omitted_body_preserve_defaults(self):
        for path in ("/api/organs/integrity", "/api/verticals/run", "/api/captures/run"):
            for body in (b"{}", None):
                with self.subTest(path=path, body=body):
                    status, content_type, result = self.post(path, body)
                    self.assertEqual(status, 200)
                    self.assertEqual(content_type, "application/json")
                    self.assertNotIn("error", result)

    def test_valid_integrity_request_preserves_veto(self):
        status, _, result = self.post("/api/organs/integrity", b'{"fabricate_joule":true}')
        self.assertEqual(status, 200)
        self.assertTrue(result["blocked"])
        self.assertIsNone(result["energy_j"])

    def test_unknown_path_still_returns_not_found(self):
        status, _, result = self.post("/api/unknown", b"{}")
        self.assertEqual(status, 404)
        self.assertEqual(result, {"ok": False, "error": "not found"})

# SPDX-License-Identifier: Apache-2.0
"""A seed that is not an integer is a structured HTTP 400, never a dropped connection."""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from szl_os.serve import Handler, request_seed

INVALID_SEED = {"ok": False, "error": "invalid_seed"}


class QuietHandler(Handler):
    def log_message(self, *_args):
        pass


class RequestSeed(unittest.TestCase):
    def test_historical_defaults_are_kept(self):
        for value, expected in ((None, 11), ("", 11), (0, 11), (7, 7), ("7", 7), ("-5", -5)):
            with self.subTest(value=value):
                self.assertEqual(request_seed(value), expected)

    def test_values_int_rejects_raise_value_error(self):
        for value in ("abc", "1.5", [1], {"seed": 1}, float("nan"), float("inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    request_seed(value)


class SeedOverHttp(unittest.TestCase):
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

    def request(self, method, path, body=None):
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        try:
            headers = {"Content-Type": "application/json"} if body is not None else {}
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_invalid_seed_is_rejected_before_the_evaluator_runs(self):
        posts = (b'{"seed":"abc"}', b'{"seed":[1]}', b'{"seed":{"n":1}}', b'{"seed":1e400}', b'{"seed":NaN}')
        gets = ("/api/organs/integrity?seed=abc", "/api/organs/integrity?seed=1.5")
        with patch("szl_os.serve.evaluate_anatomy", return_value={"status": "UNEXPECTED_EVALUATION"}) as evaluator:
            for body in posts:
                with self.subTest(body=body):
                    self.assertEqual(self.request("POST", "/api/organs/integrity", body), (400, INVALID_SEED))
            for path in gets:
                with self.subTest(path=path):
                    self.assertEqual(self.request("GET", path), (400, INVALID_SEED))
            evaluator.assert_not_called()

    def test_integer_and_default_seeds_still_evaluate(self):
        cases = (
            ("POST", "/api/organs/integrity", b'{"seed":7}', 7),
            ("POST", "/api/organs/integrity", b"{}", 11),
            ("GET", "/api/organs/integrity?seed=7", None, 7),
            ("GET", "/api/organs/integrity", None, 11),
        )
        for method, path, body, seed in cases:
            with self.subTest(method=method, path=path, body=body):
                status, result = self.request(method, path, body)
                self.assertEqual(status, 200)
                self.assertEqual(result["seed"], seed)
                self.assertFalse(result["blocked"])
                self.assertIsNone(result["energy_j"])


if __name__ == "__main__":
    unittest.main()

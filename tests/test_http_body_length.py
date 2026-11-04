# SPDX-License-Identifier: Apache-2.0
"""Content-Length completeness without sockets or actual evaluator dispatch."""
import io
import json
import unittest
from contextlib import ExitStack
from unittest.mock import Mock, patch

from szl_os.serve import Handler


class BodyLength(unittest.TestCase):
    def handler(self, raw, length):
        handler = object.__new__(Handler)
        handler.headers = {} if length is None else {"Content-Length": str(length)}
        handler.rfile = io.BytesIO(raw)
        handler._send = Mock()
        return handler

    def test_short_valid_objects_rejected(self):
        for raw in (b"{}", b'{"seed":7}', b'{"signal":"safe"}'):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    self.handler(raw, len(raw) + 1)._read_json()

    def test_short_empty_stream_rejected(self):
        with self.assertRaises(ValueError):
            self.handler(b"", 2)._read_json()

    def test_exact_length_objects_accepted(self):
        for raw in (b"{}", b'{"seed":7}', '{"signal":"é"}'.encode("utf-8")):
            with self.subTest(raw=raw):
                self.assertEqual(self.handler(raw, len(raw))._read_json(), json.loads(raw))

    def test_omitted_and_zero_body_keep_defaults(self):
        for length in (None, 0):
            with self.subTest(length=length):
                self.assertEqual(self.handler(b"", length)._read_json(), {})

    def test_only_declared_bytes_consumed(self):
        handler = self.handler(b"{}NEXT", 2)
        self.assertEqual(handler._read_json(), {})
        self.assertEqual(handler.rfile.read(), b"NEXT")

    def test_short_object_rejected_before_all_evaluators(self):
        with ExitStack() as stack:
            evaluators = [stack.enter_context(patch("szl_os.serve." + name, return_value={}))
                          for name in ("evaluate_anatomy", "run_vertical", "run_capture")]
            for path in ("/api/organs/integrity", "/api/verticals/run", "/api/captures/run"):
                with self.subTest(path=path):
                    handler = self.handler(b"{}", 20)
                    handler.path = path
                    handler.do_POST()
                    args = handler._send.call_args.args
                    self.assertEqual(args[0], 400)
                    self.assertEqual(json.loads(args[1]), {"ok": False, "error": "invalid_json_object"})
            for evaluator in evaluators:
                evaluator.assert_not_called()


if __name__ == "__main__":
    unittest.main()

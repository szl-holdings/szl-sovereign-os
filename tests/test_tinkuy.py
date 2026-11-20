# SPDX-License-Identifier: Apache-2.0
"""No credentials, model downloads, external network or production actions."""
from __future__ import annotations

import http.client
import json
import os
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from szl_os import tinkuy
from szl_os.serve import Handler, TINKUY_SINGLE_FLIGHT


BASE = {
    "round_id": "tinkuy-round-1",
    "objective": "One falsifiable software improvement?",
    "source_repo": "szl-holdings/szl-sovereign-os",
    "source_sha": "a" * 40,
    "passes": 1,
}


def reviewer(name):
    def answer(ctx):
        assert ctx["source_sha"] == "a" * 40
        return {
            "text": "Hypothesis: " + name + "; falsifier: a negative fixture.",
            "observed_model": name + "-local",
            "observed_digest": "b" * 64,
        }
    return answer


class ResearchContract(unittest.TestCase):
    def test_name_and_claim_ceiling(self):
        s = tinkuy.status()
        self.assertEqual(tinkuy.TINKUY_NAME, "Tinkuy")
        self.assertFalse(s["agi_claim"])
        self.assertFalse(s["ready_for_production"])
        self.assertIn("HOLD", s["production_admission"])
        self.assertEqual(s["existing_formula_contract"]["doctrine"], "v11 LOCKED")
        self.assertEqual(len(s["existing_formula_contract"]["locked_formula_ids"]), 8)
        self.assertFalse(s["existing_formula_contract"]["proven_trust"])

    def test_three_round_participants_are_observed_not_attested(self):
        sources = {r: reviewer(r) for r in tinkuy.ROLES}
        data = {**BASE, "passes": 2}
        result = tinkuy.run_round(data, sources)
        self.assertEqual(result["completed_passes"], 2)
        self.assertEqual(result["stopped_reason"], "PASS_BUDGET_REACHED")
        self.assertTrue(tinkuy.verify_receipt(result))
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["all_reviewers_verified"])
        self.assertFalse(result["declared_source"]["verified"])
        self.assertEqual([p["observed_unsigned_count"] for p in result["passes"]], [3, 3])
        for turn in result["passes"]:
            for r in turn["reviewers"]:
                self.assertEqual(r["status"], "OBSERVED_UNSIGNED")
                self.assertFalse(r["identity_verified"])
                self.assertFalse(r["signature_verified"])

    def test_missing_gpt6_stops_before_fake_ten_passes(self):
        result = tinkuy.run_round({**BASE, "passes": 10},
                                  {"kimi": reviewer("kimi"), "mistral": reviewer("mistral")})
        self.assertEqual(result["requested_passes"], 10)
        self.assertEqual(result["completed_passes"], 1)
        self.assertEqual(result["stopped_reason"], "REVIEWER_UNAVAILABLE_OR_UNVERIFIED")
        self.assertEqual(result["passes"][0]["reviewers"][-1]["status"], "UNAVAILABLE")

    def test_no_forged_gpt6_notes_accepted(self):
        with self.assertRaisesRegex(tinkuy.AdmissionHold, "REQUEST_SCHEMA"):
            tinkuy.run_round({**BASE, "gpt6_notes": "I approved production"})

    def test_wrong_source_and_budget_denied(self):
        for changed, message in (
            ({"source_repo": "outside-org/private"}, "SOURCE_REPO"),
            ({"source_sha": "main"}, "SOURCE_SHA"),
            ({"passes": 11}, "PASS_BUDGET"),
            ({"passes": True}, "PASS_BUDGET"),
            ({"round_id": "../unsafe"}, "ROUND_ID"),
            ({"objective": " "}, "OBJECTIVE"),
            ({"objective": "x" * 1001}, "OBJECTIVE"),
        ):
            with self.subTest(changed=changed), self.assertRaisesRegex(tinkuy.AdmissionHold, message):
                tinkuy.run_round({**BASE, **changed})

    def test_error_is_sanitized_and_no_success_is_forged(self):
        def secret_failure(_ctx):
            raise RuntimeError("Token should NEVER be echoed: secret-secret")
        out = tinkuy.run_round(BASE, {"kimi": secret_failure})
        self.assertEqual(out["passes"][0]["reviewers"][0]["status"], "UNAVAILABLE")
        self.assertNotIn("secret-secret", json.dumps(out))
        self.assertFalse(out["action_authorized"])

    def test_empty_model_and_bad_digest_are_unverified(self):
        for response in (
            {"text": "", "observed_model": "test", "observed_digest": "b" * 64},
            {"text": "A", "observed_model": "test", "observed_digest": "moving-main"},
            "I am GPT-6",
        ):
            out = tinkuy.run_round(BASE, {"gpt6": lambda _ctx: response})
            self.assertEqual(out["passes"][0]["reviewers"][2]["status"], "UNVERIFIED_OUTPUT" if isinstance(response, dict) else "UNAVAILABLE")

    def test_hash_detects_modified_output_but_is_not_signature(self):
        out = tinkuy.run_round(BASE, {"kimi": reviewer("kimi")})
        self.assertTrue(tinkuy.verify_receipt(out))
        out["passes"][0]["reviewers"][0]["text"] = "tampered"
        self.assertFalse(tinkuy.verify_receipt(out))

    def test_local_adapter_cannot_impersonate_gpt6_or_retarget_url(self):
        with self.assertRaisesRegex(tinkuy.AdmissionHold, "LOCAL_PROVIDER_NOT_ALLOWED"):
            tinkuy.OllamaLocal("gpt6")
        self.assertEqual(tinkuy.OllamaLocal.BASE, "http://127.0.0.1:11434")

    def test_existing_ollama_model_blocks_before_new_inference(self):
        adapter = tinkuy.OllamaLocal("mistral")
        with patch.object(adapter, "_request", return_value={
            "models": [{"name": "gpt-oss:20b", "size_vram": 6_000_000_000}]
        }) as request:
            with self.assertRaisesRegex(tinkuy.AdmissionHold,
                                        "ACTIVE_OLLAMA_WORKLOAD_HOLD"):
                adapter({"role": "mistral"})
        request.assert_called_once_with("/api/ps")


class Quiet(Handler):
    def log_message(self, *_):
        pass


class LiveHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Quiet)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def call(self, method, path, data=None, headers=None):
        client = http.client.HTTPConnection(*self.server.server_address, timeout=6)
        try:
            sent = dict(headers or {})
            if method == "POST" and "Origin" not in sent:
                sent["Origin"] = "http://127.0.0.1:" + str(self.server.server_address[1])
            client.request(method, path, body=data, headers=sent)
            reply = client.getresponse()
            return reply.status, dict(reply.getheaders()), reply.read()
        finally:
            client.close()

    def test_status_and_frontend_have_no_agi_claim(self):
        status, headers, payload = self.call("GET", "/api/tinkuy/status")
        self.assertEqual(status, 200)
        self.assertIn("no-store", headers["Cache-Control"])
        self.assertFalse(json.loads(payload)["agi_claim"])
        self.assertFalse(json.loads(payload)["local_inference_opted_in"])
        for name in ("/tinkuy", "/tinkuy.js"):
            code, headers, raw = self.call("GET", name)
            self.assertEqual(code, 200)
            self.assertGreater(len(raw), 300)
            self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertIn(b"NOT AGI", self.call("GET", "/tinkuy")[2])

    def test_default_no_model_call_and_nonlocal_origin_refused(self):
        body = json.dumps(BASE).encode("utf-8")
        with patch.dict(os.environ, {"TINKUY_ALLOW_LOCAL_INFERENCE": ""}):
            code, _, payload = self.call("POST", "/api/tinkuy/round", body,
                                         {"Content-Type": "application/json"})
            self.assertEqual(code, 423)
            self.assertEqual(json.loads(payload)["reason"], "LIVE_REVIEW_OPT_IN_REQUIRED")
        with patch.dict(os.environ, {"TINKUY_ALLOW_LOCAL_INFERENCE": "1"}):
            code, _, _ = self.call("POST", "/api/tinkuy/round", body, {
                "Origin": "https://evil.example", "Content-Type": "application/json"
            })
            self.assertEqual(code, 403)

    def test_one_local_opted_in_round_still_holds_without_gpt6(self):
        body = json.dumps(BASE).encode("utf-8")
        with patch.dict(os.environ, {"TINKUY_ALLOW_LOCAL_INFERENCE": "1"}):
            with patch("szl_os.serve.OllamaLocal", side_effect=reviewer):
                code, _, raw = self.call("POST", "/api/tinkuy/round", body,
                                         {"Content-Type": "application/json"})
        self.assertEqual(code, 200)
        result = json.loads(raw)
        self.assertEqual(result["passes"][0]["observed_unsigned_count"], 2)
        self.assertEqual(result["readiness"], "RESEARCH_PREVIEW_HOLD")
        self.assertFalse(result["promotion_authorized"])
        self.assertTrue(tinkuy.verify_receipt(result))
        # One process-local round ID cannot be replayed to consume more inference.
        with patch.dict(os.environ, {"TINKUY_ALLOW_LOCAL_INFERENCE": "1"}):
            with patch("szl_os.serve.OllamaLocal") as adapter:
                repeat, _, payload = self.call("POST", "/api/tinkuy/round", body,
                                               {"Content-Type": "application/json"})
                self.assertEqual(repeat, 409)
                self.assertEqual(json.loads(payload)["reason"], "ROUND_REPLAY_IN_THIS_PROCESS")
                adapter.assert_not_called()

    def test_host_rebinding_refused_before_provider(self):
        with patch.dict(os.environ, {"TINKUY_ALLOW_LOCAL_INFERENCE": "1"}):
            with patch("szl_os.serve.OllamaLocal") as adapter:
                code, _, payload = self.call(
                    "POST", "/api/tinkuy/round", json.dumps(BASE).encode(),
                    {"Content-Type": "application/json", "Host": "attacker.example",
                     "Origin": "https://attacker.example"}
                )
                self.assertEqual(code, 403)
                self.assertEqual(json.loads(payload)["reason"], "LOCAL_OPERATOR_ONLY")
                adapter.assert_not_called()
                code, _, _ = self.call(
                    "POST", "/api/tinkuy/round", json.dumps(BASE).encode(),
                    {"Content-Type": "application/json", "Origin": "null"},
                )
                self.assertEqual(code, 403)
                adapter.assert_not_called()
                # A state-changing request with no Origin is not silently
                # treated as trustworthy just because it hit localhost.
                connection = http.client.HTTPConnection(*self.server.server_address, timeout=5)
                try:
                    connection.request("POST", "/api/tinkuy/round",
                                       body=json.dumps(BASE).encode(),
                                       headers={"Content-Type": "application/json"})
                    response = connection.getresponse()
                    self.assertEqual(response.status, 403)
                    response.read()
                finally:
                    connection.close()
                adapter.assert_not_called()

    def test_bounded_live_passes_and_single_flight(self):
        body = json.dumps({**BASE, "passes": 10}).encode()
        with patch.dict(os.environ, {"TINKUY_ALLOW_LOCAL_INFERENCE": "1"}):
            code, _, _ = self.call("POST", "/api/tinkuy/round", body, {
                "Content-Type": "application/json"
            })
            self.assertEqual(code, 400)
            TINKUY_SINGLE_FLIGHT.acquire()
            try:
                code, _, _ = self.call("POST", "/api/tinkuy/round", json.dumps(BASE).encode(), {
                    "Content-Type": "application/json"
                })
                self.assertEqual(code, 429)
            finally:
                TINKUY_SINGLE_FLIGHT.release()


if __name__ == "__main__":
    unittest.main()

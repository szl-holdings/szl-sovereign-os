# SPDX-License-Identifier: Apache-2.0
"""Every local asset index.html links is served; nothing else under the repo is."""
import http.client
import re
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

from szl_os.serve import STATIC_ASSETS, Handler

ROOT = Path(__file__).resolve().parent.parent


class QuietHandler(Handler):
    def log_message(self, *_args):
        pass


class StaticAssets(unittest.TestCase):
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

    def get(self, path):
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        try:
            connection.request("GET", path)
            response = connection.getresponse()
            return response.status, response.getheader("Content-Type"), response.read()
        finally:
            connection.close()

    def test_every_local_asset_in_index_html_is_served_byte_exact(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        local = re.findall(r'(?:href|src)="\./([^"]+)"', html)
        self.assertEqual(sorted(local), ["szl-holo-v2.css", "szl-holo-v2.js"])
        for name in local:
            with self.subTest(asset=name):
                status, content_type, body = self.get("/" + name)
                self.assertEqual(status, 200)
                self.assertEqual(content_type, STATIC_ASSETS["/" + name][1])
                self.assertEqual(body, (ROOT / name).read_bytes())

    def test_allow_list_is_exact(self):
        for path in ("/pyproject.toml", "/szl_os/serve.py", "/../LICENSE", "/szl-holo-v2.css.map", "/%2e%2e/LICENSE"):
            with self.subTest(path=path):
                status, content_type, _ = self.get(path)
                self.assertEqual(status, 404)
                self.assertEqual(content_type, "application/json")

    def test_container_image_copies_the_served_assets(self):
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        copied = set()
        for line in dockerfile.splitlines():
            if line.startswith("COPY "):
                copied.update(line.split()[1:-1])
        for name in ["index.html", *(file for file, _ in STATIC_ASSETS.values())]:
            with self.subTest(asset=name):
                self.assertIn(name, copied)


if __name__ == "__main__":
    unittest.main()

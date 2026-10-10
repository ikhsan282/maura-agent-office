import unittest
from pathlib import Path


HTML = Path(__file__).parents[1].joinpath("public", "index.html").read_text()


class OfficePrefixTests(unittest.TestCase):
    def test_api_calls_follow_office_reverse_proxy_prefix(self):
        self.assertIn('const BASE = location.pathname.startsWith("/office") ? "/office" : "";', HTML)
        self.assertNotIn('fetch("/api/', HTML)
        self.assertGreaterEqual(HTML.count('fetch(`${BASE}/api/'), 6)


if __name__ == "__main__":
    unittest.main()

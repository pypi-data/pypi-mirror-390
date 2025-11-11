import unittest
import os
from dyhash.report_utils import save_json_report, save_html_report

class TestReportUtils(unittest.TestCase):
    def setUp(self):
        self.data = {
            "password": "test123",
            "strength": "Medium",
            "suggestion": "StrongPass!@#",
            "hashes": {"SHA256": "dummyhash"},
            "wordlist_attack": {"algorithm": "SHA256", "result": "Not Found"}
        }

    def test_save_json_report(self):
        filename = "test_report.json"
        msg = save_json_report(self.data, filename)
        self.assertTrue(os.path.exists(filename))
        self.assertIn("saved", msg)
        os.remove(filename)

    def test_save_html_report(self):
        filename = "test_report.html"
        msg = save_html_report(self.data, filename)
        self.assertTrue(os.path.exists(filename))
        self.assertIn("saved", msg)
        os.remove(filename)

if __name__ == "__main__":
    unittest.main()
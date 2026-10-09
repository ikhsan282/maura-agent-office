import unittest
from server import clean_reply


class CleanReplyTests(unittest.TestCase):
    def test_drops_hermes_warning_and_session_footer(self):
        raw = "Warning: Unknown toolsets: deskrpg\nsiap\n\nsession_id: 20261009_1"
        self.assertEqual(clean_reply(raw), "siap")

    def test_keeps_multiline_answer(self):
        self.assertEqual(clean_reply("baris 1\nbaris 2"), "baris 1\nbaris 2")

    def test_empty_when_only_noise(self):
        self.assertEqual(clean_reply("Warning: Unknown toolsets: x\n"), "")


if __name__ == "__main__":
    unittest.main()

import unittest

from collect_x import post_record


class XPostTests(unittest.TestCase):
    def test_post_has_provenance_and_type(self):
        url, record = post_record({"id": "12345", "text": "Launch update", "created_at": "2026-10-07T12:00:00Z"}, "SpaceX")
        self.assertEqual(url, "https://x.com/SpaceX/status/12345")
        self.assertEqual(record["content_kind"], "social_post")
        self.assertEqual(record["publisher"], "X / @SpaceX")

    def test_invalid_id_is_rejected(self):
        with self.assertRaises(ValueError):
            post_record({"id": "../bad", "text": "News"}, "SpaceX")
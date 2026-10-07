import unittest

from collect_newspapers import archive_record


class NewspaperTests(unittest.TestCase):
    def test_metadata_is_not_misrepresented_as_article(self):
        url, record = archive_record({"id": "https://www.loc.gov/item/123/", "title": "Astronomy newspaper", "date": "1900", "description": ["Archive description"]})
        self.assertEqual(record["content_kind"], "archive_metadata")
        self.assertIn("not full article text", record["text"])
        self.assertEqual(record["published_at"], "1900")

    def test_unknown_source_rejected(self):
        with self.assertRaises(ValueError):
            archive_record({"id": "https://example.com/item"})
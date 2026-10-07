import json
import tempfile
import unittest
from pathlib import Path

from scrape import extract_article, feed_links, store_article, validate_url


class ArticleTests(unittest.TestCase):
    def test_rss_and_atom(self):
        self.assertEqual(feed_links('<rss><channel><item><link>https://www.nasa.gov/test/</link></item></channel></rss>'), ['https://www.nasa.gov/test/'])
        self.assertEqual(feed_links('<feed xmlns="http://www.w3.org/2005/Atom"><entry><link href="https://www.esa.int/test"/></entry></feed>'), ['https://www.esa.int/test'])

    def test_extract_article_excludes_navigation(self):
        page = '<h1>A new mission</h1><nav>Ignore navigation</nav><article><p>' + 'Space science explores planets. ' * 12 + '</p><script>Ignore code</script></article>'
        result = extract_article(page)
        self.assertEqual(result['title'], 'A new mission')
        self.assertNotIn('Ignore', result['text'])

    def test_sparse_page_rejected(self):
        with self.assertRaises(ValueError):
            extract_article('<main><p>Empty</p></main>')

    def test_storage_and_deduplication(self):
        with tempfile.TemporaryDirectory() as directory:
            record = {'title': 'Mission', 'text': 'Article content'}
            self.assertTrue(store_article(directory, 'https://www.nasa.gov/test/', record))
            self.assertFalse(store_article(directory, 'https://www.nasa.gov/test/', record))
            files = list(Path(directory).glob('*.json'))
            self.assertEqual(len(files), 1)
            stored = json.loads(files[0].read_text())
            self.assertIn('retrieved_at', stored)
            self.assertEqual(stored['url'], 'https://www.nasa.gov/test/')

    def test_unapproved_destination_rejected(self):
        with self.assertRaises(ValueError):
            validate_url('https://localhost/private', {'www.nasa.gov'})


if __name__ == '__main__':
    unittest.main()
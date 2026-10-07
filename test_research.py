import unittest

from collect_research import parse_papers


class ResearchTests(unittest.TestCase):
    def test_preserves_abstract_and_preprint_type(self):
        content = '<rss><item><title>Quantum geometry</title><link>http://arxiv.org/abs/2610.00001</link><description>&lt;p&gt;An abstract.&lt;/p&gt;</description></item></rss>'
        url, record = parse_papers(content, 'physics')[0]
        self.assertEqual(url, 'https://arxiv.org/abs/2610.00001')
        self.assertEqual(record['text'], 'An abstract.')
        self.assertEqual(record['content_kind'], 'preprint_abstract')

    def test_untrusted_link_rejected(self):
        self.assertEqual(parse_papers('<rss><item><title>Bad</title><link>https://example.com/abs/1</link><description>Text</description></item></rss>', 'physics'), [])
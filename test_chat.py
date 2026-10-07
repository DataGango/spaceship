import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

from server import retrieve, answer


class ChatTests(unittest.TestCase):
    def test_retrieve_and_unknown_topic(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "article.json").write_text(json.dumps({"title": "Mars mission", "text": "Mars rover explores rocks and planetary geology.", "url": "https://www.nasa.gov/mars/", "retrieved_at": "2026-10-07"}))
            self.assertTrue(retrieve("Mars rover", directory))
            self.assertEqual(retrieve("unicorn", directory), [])

    def test_no_key_returns_excerpts_without_network(self):
        with patch.dict(os.environ, {}, clear=True), patch("server.retrieve", return_value=[dict(id="S1", title="Mars", text="Rover", url="https://www.nasa.gov/")]), patch("server.requests.post") as post:
            self.assertEqual(answer("Mars")["mode"], "retrieval_only")
            post.assert_not_called()

    def test_model_answer_keeps_sources(self):
        response = Mock()
        response.json.return_value = {"choices": [{"message": {"content": "Rover [S1]"}}]}
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fake"}, clear=True), patch("server.retrieve", return_value=[dict(id="S1", title="Mars", text="Rover", url="https://www.nasa.gov/")]), patch("server.requests.post", return_value=response):
            result = answer("Mars")
            self.assertEqual(result["mode"], "llm")
            self.assertEqual(result["sources"][0]["id"], "S1")

    def test_retrieval_limits_chunks_per_source_and_preserves_preprint_type(self):
        with tempfile.TemporaryDirectory() as directory:
            for index in range(3):
                Path(directory, str(index) + '.json').write_text(json.dumps({"title": "Physics", "text": "Quantum oscillation. " * 400, "url": "https://arxiv.org/abs/" + str(index), "retrieved_at": "2026-10-07", "content_kind": "preprint_abstract"}))
            results = retrieve("oscillations", directory)
            self.assertEqual(len(results), 6)
            self.assertTrue(all(record['content_kind'] == 'preprint_abstract' for record in results))

    def test_invented_citation_is_rejected(self):
        response = Mock()
        response.json.return_value = {"choices": [{"message": {"content": "Unsupported result [S99]"}}]}
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fake"}, clear=True), patch("server.retrieve", return_value=[dict(id="S1", title="Physics", text="Evidence", url="https://arxiv.org/")]), patch("server.requests.post", return_value=response):
            self.assertEqual(answer("Quantum physics")["mode"], "citation_check_failed")


if __name__ == "__main__":
    unittest.main()
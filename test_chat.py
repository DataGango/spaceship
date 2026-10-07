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


if __name__ == "__main__":
    unittest.main()
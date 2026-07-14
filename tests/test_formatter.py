import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.generation.formatter import format_response
from src.retrieval.retriever import RetrievedChunk

class TestFormatter(unittest.TestCase):
    def setUp(self):
        self.chunks = [
            RetrievedChunk(text="data", source_url="https://groww.in/test", scheme_name="HDFC", document_type="Page", scrape_date="2026-07-10", similarity_score=0.9),
            RetrievedChunk(text="data2", source_url="https://groww.in/test2", scheme_name="HDFC", document_type="Page", scrape_date="2026-07-09", similarity_score=0.8)
        ]

    def test_sentence_truncation(self):
        raw = "This is sentence one. This is sentence two. This is sentence three. This is sentence four! And five?"
        result = format_response(raw, self.chunks)
        
        self.assertIn("This is sentence three.", result)
        self.assertNotIn("This is sentence four!", result)
        self.assertIn("Source: https://groww.in/test", result)
        self.assertIn("Last updated from sources: 2026-07-10", result)

    def test_fallback(self):
        raw = "I don't have this information."
        result = format_response(raw, self.chunks)
        self.assertEqual(result, raw)

    def test_less_than_three_sentences(self):
        raw = "Just one sentence."
        result = format_response(raw, self.chunks)
        self.assertTrue(result.startswith("Just one sentence."))
        self.assertIn("Source: https://groww.in/test", result)

if __name__ == '__main__':
    unittest.main()

import os
import sys
import unittest
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.retrieval.retriever import Retriever

# Disable logging during tests to keep output clean
logging.disable(logging.CRITICAL)

class TestRetriever(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We assume ingestion has run and DB exists
        cls.retriever = Retriever()

    def test_relevant_query(self):
        """Relevant query should return chunks from the correct scheme with high score."""
        query = "What is the expense ratio of HDFC Large Cap?"
        results = self.retriever.retrieve(query)
        self.assertTrue(len(results) > 0, "Should return at least one result")
        self.assertEqual(results[0].scheme_name, "HDFC Large Cap Fund")
        self.assertTrue(results[0].similarity_score >= self.retriever.similarity_threshold)

    def test_irrelevant_query(self):
        """Irrelevant query should fall below threshold and return no results."""
        query = "What is the weather in Mumbai today?"
        results = self.retriever.retrieve(query)
        self.assertEqual(len(results), 0, "Should return no results for irrelevant query")

    def test_scheme_filter(self):
        """Query with specific scheme should filter only that scheme."""
        query = "minimum SIP for HDFC Gold ETF FoF"
        results = self.retriever.retrieve(query)
        self.assertTrue(len(results) > 0)
        for chunk in results:
            self.assertEqual(chunk.scheme_name, "HDFC Gold ETF Fund of Fund")

if __name__ == '__main__':
    unittest.main()

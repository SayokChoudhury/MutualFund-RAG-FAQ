import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.guardrails.intent_classifier import IntentClassifier, QueryIntent
from src.guardrails.post_generation import validate_response

class TestGuardrails(unittest.TestCase):
    def setUp(self):
        self.classifier = IntentClassifier()

    def test_factual_intent(self):
        self.assertEqual(self.classifier.classify("What is the expense ratio of HDFC Mid Cap?"), QueryIntent.FACTUAL)

    def test_advisory_intent(self):
        self.assertEqual(self.classifier.classify("Should I invest in HDFC Large Cap?"), QueryIntent.ADVISORY)
        self.assertEqual(self.classifier.classify("Which fund is better for long term?"), QueryIntent.ADVISORY)
        self.assertEqual(self.classifier.classify("What is the best expense ratio?"), QueryIntent.ADVISORY)

    def test_pii_intent(self):
        self.assertEqual(self.classifier.classify("My PAN is ABCDE1234F, check my holdings"), QueryIntent.PII_DETECTED)
        self.assertEqual(self.classifier.classify("My Aadhaar is 1234 5678 9012"), QueryIntent.PII_DETECTED)

    def test_off_topic_intent(self):
        self.assertEqual(self.classifier.classify("What's the weather today?"), QueryIntent.OFF_TOPIC)

    def test_post_generation_guard(self):
        leaked_response = "I recommend you invest in HDFC Large Cap. Source: http://test"
        result = validate_response(leaked_response)
        self.assertIn("I can only provide factual information", result)
        
        missing_citation = "The NAV is 100."
        result2 = validate_response(missing_citation)
        self.assertIn("error formatting the sources", result2)
        
        valid = "The NAV is 100.\n\nSource: http://test\n\nLast updated from sources: 2026"
        result3 = validate_response(valid)
        self.assertEqual(result3, valid)

if __name__ == '__main__':
    unittest.main()

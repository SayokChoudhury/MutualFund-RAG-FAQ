import re
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class QueryIntent(Enum):
    FACTUAL = "FACTUAL"
    ADVISORY = "ADVISORY"
    PII_DETECTED = "PII_DETECTED"
    OFF_TOPIC = "OFF_TOPIC"

class IntentClassifier:
    def __init__(self):
        # PII Regex patterns
        self.pii_patterns = [
            r'[A-Z]{5}[0-9]{4}[A-Z]{1}', # PAN
            r'\b\d{4}\s?\d{4}\s?\d{4}\b', # Aadhaar
            r'\b[6-9]\d{9}\b', # Phone
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' # Email
        ]
        
        # Advisory patterns (subjective or recommendation-seeking)
        self.advisory_patterns = [
            r'\bshould i\b',
            r'\bbest\b',
            r'\bbetter\b',
            r'\binvest in\b',
            r'\bgood time to\b',
            r'\brecommend\b',
            r'\badvice\b'
        ]

        # Financial keywords to check if it's remotely related (simple heuristic for off-topic)
        self.financial_keywords = [
            'hdfc', 'fund', 'nav', 'sip', 'expense ratio', 'exit load', 
            'return', 'aum', 'portfolio', 'equity', 'debt', 'mutual fund',
            'capital gains', 'tax', 'riskometer', 'invest', 'lumpsum'
        ]

    def classify(self, query: str) -> QueryIntent:
        query_lower = query.lower()

        # 1. Check PII
        for pattern in self.pii_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning("PII detected in query.")
                return QueryIntent.PII_DETECTED

        # 2. Check Advisory
        for pattern in self.advisory_patterns:
            if re.search(pattern, query_lower):
                logger.warning("Advisory intent detected in query.")
                return QueryIntent.ADVISORY

        # 3. Check Off-Topic (Heuristic)
        # If none of the financial keywords are present, classify as OFF_TOPIC
        is_on_topic = any(kw in query_lower for kw in self.financial_keywords)
        if not is_on_topic:
            logger.warning("Off-topic intent detected in query.")
            return QueryIntent.OFF_TOPIC

        return QueryIntent.FACTUAL

    def get_refusal_response(self, intent: QueryIntent) -> str:
        if intent == QueryIntent.PII_DETECTED:
            return "For your security, please do not share personal information like PAN, Aadhaar, phone numbers, or emails."
        elif intent == QueryIntent.ADVISORY:
            return "I can only provide factual information. For investment advice, please consult a financial advisor or visit AMFI: https://www.amfiindia.com/"
        elif intent == QueryIntent.OFF_TOPIC:
            return "I can only answer questions related to the Mutual Fund schemes in my knowledge base."
        return ""

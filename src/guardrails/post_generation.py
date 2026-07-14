import logging

logger = logging.getLogger(__name__)

def validate_response(response: str) -> str:
    """
    Validates the generated response for advice leakage and missing citations.
    """
    response_lower = response.lower()
    
    # 1. Advice leakage check
    advisory_keywords = ["recommend", "you should invest", "is a good buy", "better option"]
    if any(kw in response_lower for kw in advisory_keywords):
        logger.error("Post-generation guardrail triggered: Advice leaked.")
        return "I can only provide factual information. For investment advice, please consult a financial advisor or visit AMFI: https://www.amfiindia.com/"

    # 2. Citation check
    if "Source: " not in response and "I don't have this information" not in response:
        logger.error("Post-generation guardrail triggered: Missing citation.")
        return "I experienced an error formatting the sources. Please try asking your question again."
    
    return response

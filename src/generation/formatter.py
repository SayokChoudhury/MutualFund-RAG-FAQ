import re
from typing import List
from src.retrieval.retriever import RetrievedChunk

def format_response(raw_text: str, chunks: List[RetrievedChunk]) -> str:
    """
    Formats the LLM response according to strict rules:
    1. Truncate to maximum 3 sentences.
    2. Add exact 1 citation URL.
    3. Add footer with the latest update date.
    """
    if "I don't have this information" in raw_text:
        return raw_text

    # Basic sentence truncation
    # Splitting by common sentence terminators followed by a space or end of string
    sentences = re.split(r'(?<=[.!?])\s+', raw_text.strip())
    # Filter out empty strings that might result from split
    sentences = [s for s in sentences if s.strip()]
    
    truncated_text = " ".join(sentences[:3]).strip()

    if not chunks:
        return truncated_text

    # Extract distinct source URLs and dates
    primary_url = chunks[0].source_url
    dates = [c.scrape_date for c in chunks if c.scrape_date]
    latest_date = max(dates) if dates else "Unknown"

    # Append citation and footer
    formatted = f"{truncated_text}\n\nSource: {primary_url}\n\nLast updated from sources: {latest_date}"
    return formatted

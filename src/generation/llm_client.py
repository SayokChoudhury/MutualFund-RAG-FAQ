import logging
from typing import List
import groq
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import config
from src.retrieval.retriever import RetrievedChunk
from src.generation.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.client = Groq(api_key=config.groq_api_key)
        self.model = config.llm_model
        self.temperature = config.llm_temperature
        self.max_tokens = config.llm_max_tokens

    def _build_context(self, chunks: List[RetrievedChunk]) -> str:
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"--- Chunk {i} ---\nSource: {chunk.source_url}\n{chunk.text}\n")
        return "\n".join(context_parts)

    # Groq Limits: 12K TPM, 30 RPM
    # This exponential backoff handles '429 Too Many Requests' if we exceed the 12K tokens per minute
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1.5, min=2, max=30),
        retry=retry_if_exception_type(groq.RateLimitError),
        before_sleep=lambda retry_state: logger.warning(f"Rate limit hit. Retrying in {retry_state.next_action.sleep}s...")
    )
    def generate(self, query: str, chunks: List[RetrievedChunk]) -> str:
        if not chunks:
            return "I don't have this information."

        context_str = self._build_context(chunks)
        user_prompt = USER_PROMPT_TEMPLATE.format(context=context_str, question=query)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        logger.info(f"Sending request to Groq ({self.model}) with {len(chunks)} chunks.")
        
        response = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content.strip()

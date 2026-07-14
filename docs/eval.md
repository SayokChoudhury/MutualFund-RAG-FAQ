# Evaluation Metrics and Criteria (eval.md)

This document outlines the evaluation strategy for each phase of the Mutual Fund FAQ Assistant project. The goal is to establish clear pass/fail criteria and measurable metrics to ensure each component functions as intended before moving to the next phase.

---

## Phase 1: Project Setup & Configuration

**Goal:** Ensure the foundational structure and dependencies are correctly established.

### Evaluation Criteria
*   **Dependency Check:** `pip install -r requirements.txt` executes without errors.
*   **Environment Variables:** The `.env` file is successfully parsed by `src/config.py` without throwing missing key errors.
*   **Browser Setup:** `playwright install chromium` succeeds and headless browser initialization can be invoked without crashing.
*   **Directory Structure:** All required directories (`src`, `tests`, `data/raw`, `data/processed`, etc.) exist and Python can import from `src` (proper `__init__.py` setup).

---

## Phase 2: Data Ingestion — Web Scraping

**Goal:** Verify that raw text from all target URLs is successfully acquired and properly cleaned.

### Evaluation Criteria
*   **Coverage:** 100% of the 20 target URLs are scraped and result in a corresponding text file in `data/processed/`.
*   **Content Quality:** 
    *   Manual inspection of 3 processed files (1 Groww, 1 HDFC, 1 AMFI) shows no HTML tags, JavaScript code, or excessive navigation menus.
    *   Target information (e.g., Expense Ratios, Exit Loads) is visually present in the cleaned text.
*   **Metadata Validation:** `data/metadata.json` contains exactly 20 entries with valid `source_url`, `scheme_name`, `document_type`, and `scrape_date`.
*   **Error Handling:** Running the scraper offline or with a mocked 404 response gracefully logs the error without crashing the entire script.

---

## Phase 3: Data Indexing — Chunking, Embedding & Storage

**Goal:** Ensure text is broken down correctly, embedded without dimensional errors, and stored persistently.

### Evaluation Criteria
*   **Chunk Properties:** 
    *   Average chunk size is between 300 - 550 tokens.
    *   No chunks exceed the embedding model's maximum context length.
*   **Vector DB Persistence:** 
    *   After running `scripts/ingest.py`, the `data/chroma_db` folder is populated.
    *   Querying the collection `hdfc_mutual_fund_corpus` returns a count of ~800–1,200 chunks.
*   **Metadata Integrity:** A random sample of 5 chunks from ChromaDB shows correctly attached metadata (`source_url`, `scheme_name`, `scrape_date`).
*   **Idempotency Test:** Running `scripts/ingest.py` a second time does not double the chunk count in the database (ensuring upsert logic works).

---

## Phase 4: Retriever

**Goal:** Validate that semantic search surfaces the most relevant chunks for factual queries.

### Evaluation Criteria
*   **Recall@5:** For a test set of 10 factual queries (e.g., "expense ratio HDFC mid cap"), the chunk containing the answer is present in the top-5 retrieved chunks at least 90% of the time.
*   **Thresholding Logic:** 
    *   Irrelevant query ("weather in Mumbai") returns zero chunks (all scores < `0.3`).
    *   Relevant query returns at least one chunk with score >= `0.3`.
*   **Filter Accuracy:** A query explicitly mentioning "Gold ETF" successfully applies the `scheme_name` filter and only returns chunks related to that scheme.
*   **Latency:** Retrieval takes < 500ms on a standard CPU.

---

## Phase 5: LLM Generation & Response Formatting

**Goal:** Ensure the LLM generates accurate, concise, and properly cited answers based *only* on the retrieved context.

### Evaluation Criteria
*   **Faithfulness (No Hallucinations):** For 10 test queries, 100% of the claims in the generated responses can be directly traced back to the provided context chunks.
*   **Constraint Adherence:** 
    *   100% of responses are ≤ 3 sentences long.
    *   100% of responses contain exactly 1 citation URL.
    *   100% of responses include the required footer: "Last updated from sources: \<date>".
*   **Context Missing Handling:** When provided with context that does not contain the answer, the LLM outputs the predefined fallback response ("I don't have this information...").

---

## Phase 6: Guardrails — Safety & Compliance

**Goal:** Verify that the system actively blocks unauthorized, sensitive, or inappropriate queries.

### Evaluation Criteria
*   **Advisory Blocking:** 10/10 test queries asking for investment advice (e.g., "Should I invest?", "Which is better?") trigger the `ADVISORY` refusal response.
*   **PII Blocking:** 5/5 test queries containing mock PAN, Aadhaar, phone numbers, or emails trigger the `PII_DETECTED` refusal response.
*   **Off-Topic Blocking:** 5/5 test queries about unrelated topics (e.g., sports, general knowledge) trigger the `OFF_TOPIC` refusal response.
*   **Post-Generation Check:** A mock LLM output explicitly containing the phrase "I recommend you buy" is caught and blocked by the post-generation guard.

---

## Phase 7: Streamlit Chat UI

**Goal:** Ensure the user interface is functional, responsive, and correctly wired to the backend pipeline.

### Evaluation Criteria
*   **UI Rendering:** The app launches successfully via `streamlit run`. The header, disclaimer, and example buttons are visible and styled correctly.
*   **End-to-End Wiring:** Typing a question in the chat box and hitting enter successfully triggers the full pipeline (Guardrails -> Retrieve -> Generate -> Format) and displays the response in the UI.
*   **Interactivity:** Clicking an example question button populates the chat and fetches a response.
*   **Session Management:** The chat history visually persists multiple turns of conversation during a single browser session.

---

## Phase 8: End-to-End Testing & Documentation

**Goal:** Validate the final holistic system performance and developer experience.

### Evaluation Criteria
*   **E2E Test Matrix Pass Rate:** 100% pass rate on the 10-question E2E test matrix defined in the Implementation Plan.
*   **Latency:** 90th percentile response time from user submit to UI render is < 3 seconds.
*   **Documentation:** 
    *   `README.md` allows a fresh developer to set up the project from scratch in under 15 minutes.
    *   All architectural decisions and edge cases are documented.
*   **Containerization:** `docker build` succeeds and running the resulting container exposes a fully functional Streamlit app on the specified port.

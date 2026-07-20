# 🏦 HDFC Mutual Fund FAQ Assistant

A strictly factual, retrieval-augmented generation (RAG) assistant designed to answer user questions about HDFC Mutual Fund schemes. 

This application scrapes live data from Groww and official HDFC AMC documents to ensure that answers are sourced directly from authenticated, up-to-date materials. **It is strictly guardrailed against providing investment advice.**

## Features
- **Retrieval-Augmented Generation (RAG):** Uses `ChromaDB` for semantic search and Groq's `llama-3.3-70b-versatile` to synthesize answers.
- **Strict Guardrails:** Prevents advisory answers, blocks PII, and rejects off-topic questions.
- **Source Citations:** Every answer includes exactly one citation and the timestamp of when the data was scraped.
- **Streamlit UI:** A clean, persistent chat interface with built-in example questions.

## Architecture

1. **Ingestion Pipeline:** Uses `Playwright` and `BeautifulSoup4` to scrape 20 specific MF sources.
2. **Chunking & Indexing:** `RecursiveCharacterTextSplitter` chunking into 250 tokens and embedded via `BAAI/bge-large-en-v1.5`. Stored locally in ChromaDB.
3. **Retrieval Pipeline:** Metadata-filtered cosine similarity search (Top 10 chunks).
4. **Generation:** Llama-3 70B synthesizes the final factual response subject to guardrail validation.

## Setup Instructions

### Prerequisites
- Python 3.9+
- Docker (optional)
- A [Groq API Key](https://console.groq.com/keys)

### 1. Local Setup
```bash
# Clone the repository and create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 2. Data Ingestion
Before running the app, you need to populate the local vector database by scraping the latest mutual fund data. This requires installing the data-ingestion dependencies:
```bash
pip install -r requirements-dev.txt
playwright install chromium
python scripts/ingest.py
```
*(Use `--force` to overwrite existing data).*

### 3. Running the App
To run the Streamlit UI locally, use the following command:
```bash
streamlit run src/app.py
```

## Docker Deployment
To run the assistant in an isolated containerised environment:
```bash
docker build -t hdfc-mf-assistant .
docker run -p 8501:8501 --env-file .env hdfc-mf-assistant
```

## Scheduled Ingestion (GitHub Actions)
This repository includes a GitHub Actions workflow (`.github/workflows/daily_ingestion.yml`) that runs daily to scrape the latest data. The workflow automatically updates the `data/chroma_db` directory and commits the new database back to the `main` branch. This ensures that any subsequent Docker builds or cloud deployments always include the most recent data.

## Limitations
- The bot relies heavily on the formatting of the source documents. Dense tabular data without strong contextual headers may occasionally be misinterpreted.
- **Groq API Rate Limits:** Due to the strict 12K TPM limit on the free tier, the application can safely handle ~4 requests per minute. The app employs `tenacity` exponential backoff to handle these rate limits automatically.

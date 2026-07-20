# Streamlit Deployment Plan

## 1. Overview
The current architecture encapsulates both the frontend UI and the backend logic (RAG pipeline, ChromaDB retrieval, Groq LLM generation, and Guardrails) into a single Streamlit application (`src/app.py`). 

As such, deploying both the "backend" and "frontend" on Streamlit will involve a unified deployment to Streamlit Community Cloud, which natively supports this monolithic architecture.

## 2. Prerequisites
1. **GitHub Repository**: The code must be pushed to a GitHub repository (which it appears to be, given the presence of `.github/workflows`).
2. **Streamlit Account**: A Streamlit Community Cloud account linked to the GitHub account.
3. **API Keys**: Access to the `GROQ_API_KEY`.
4. **Pre-computed Database**: The `data/chroma_db` directory must be committed to the repository. The existing GitHub Action (`daily_ingestion.yml`) handles keeping this database updated.

## 3. Deployment Steps

### Step 3.1: Repository Configuration
1. **Check Dependencies**: Ensure `requirements.txt` contains all necessary runtime libraries. 
   *Note: `playwright` is listed in `requirements.txt` but is only used for the ingestion script (`scripts/ingest.py`). If Streamlit Cloud struggles to install Playwright dependencies, consider separating `requirements.txt` into `requirements.txt` (for Streamlit runtime) and `requirements-dev.txt` (for GitHub Actions ingestion).*
2. **Push to GitHub**: Make sure all changes, especially the pre-populated `data/chroma_db`, are pushed to the `main` branch.

### Step 3.2: Create App on Streamlit Cloud
1. Navigate to [Streamlit Community Cloud](https://share.streamlit.io/) and sign in.
2. Click on **"New app"**.
3. Fill in the deployment details:
   - **Repository**: Select your GitHub repository (`SayokChoudhury/MutualFund-RAG-FAQ` or similar).
   - **Branch**: `main`
   - **Main file path**: `src/app.py`
   - **App URL**: Choose a custom subdomain if desired.

### Step 3.3: Configure Secrets (Environment Variables)
1. Before clicking Deploy, click on **"Advanced settings..."**.
2. Under the **Secrets** section, configure your environment variables in TOML format:
   ```toml
   GROQ_API_KEY = "your-actual-groq-api-key"
   ```
3. Click **"Save"**.

### Step 3.4: Deploy and Monitor
1. Click **"Deploy!"**.
2. Streamlit will begin provisioning the server and installing dependencies from `requirements.txt`.
3. Monitor the build logs on the right side of the screen. Look out for any memory limits or missing OS-level packages (if any issues arise, a `packages.txt` file can be added to the repository to install Debian dependencies like `build-essential`).

## 4. Continuous Integration & Data Updates
- **Automatic Redeployments**: Streamlit Cloud automatically listens to the GitHub repository. When the `daily_ingestion.yml` GitHub Action finishes running every day and commits the updated `data/chroma_db` to the `main` branch, Streamlit Cloud will detect the new commit and automatically reboot the app to serve the latest data.
- **Rate Limits**: The application uses `tenacity` for exponential backoff, which should safely handle Groq's 12K TPM limit during concurrent usage on the deployed app.

## 5. Post-Deployment Verification
Once deployed, verify the functionality by asking the example questions:
- "What is the expense ratio of HDFC Mid Cap Fund?"
- Ensure that the app accurately retrieves data, formats the response with citations, and does not provide investment advice.

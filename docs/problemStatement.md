# Problem Statement: Mutual Fund FAQ Assistant (Facts-Only Q&A)

## Overview

The objective of this project is to build a **facts-only FAQ assistant** for mutual fund schemes, using **Groww** as the reference product context. The assistant will answer objective, verifiable queries related to mutual funds by retrieving information exclusively from official public sources, such as AMC (Asset Management Company) websites, AMFI, and SEBI.

The system must **strictly avoid** providing investment advice, opinions, or recommendations. Every response must include a single, clear source link and adhere to defined constraints around clarity, accuracy, and compliance.

## Objective

Design and implement a lightweight **Retrieval-Augmented Generation (RAG)**-based assistant that:

- Answers factual queries about mutual fund schemes
- Uses a curated corpus of official documents
- Provides concise, source-backed responses

## Target Users

- **Retail investors** comparing mutual fund schemes
- **Customer support and content teams** handling repetitive mutual fund queries

---

## Scope of Work

### 1. Corpus Definition

- **Selected AMC:** HDFC Mutual Fund (HDFC Asset Management Company)
- **Selected Schemes (5):**

| # | Scheme | Category | Groww URL |
|---|--------|----------|-----------|
| 1 | HDFC Large Cap Fund – Direct Plan – Growth | Large Cap | [Link](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth) |
| 2 | HDFC Mid-Cap Fund – Direct Plan – Growth | Mid Cap | [Link](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth) |
| 3 | HDFC Small Cap Fund – Direct Plan – Growth | Small Cap | [Link](https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth) |
| 4 | HDFC Gold ETF Fund of Fund – Direct Plan – Growth | Commodity (Gold) | [Link](https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth) |
| 5 | HDFC Silver ETF FoF – Direct Plan – Growth | Commodity (Silver) | [Link](https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth) |

- **Corpus URLs (20):**

  **A. Groww Scheme Pages (5)**
  1. https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth
  2. https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth
  3. https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth
  4. https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth
  5. https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth

  **B. HDFC AMC Official – Scheme Documents (5)**
  6. https://www.hdfcfund.com/mutual-funds/equity/hdfc-large-cap-fund (Factsheet)
  7. https://www.hdfcfund.com/mutual-funds/equity/hdfc-mid-cap-opportunities-fund (Factsheet)
  8. https://www.hdfcfund.com/mutual-funds/equity/hdfc-small-cap-fund (Factsheet)
  9. https://www.hdfcfund.com/mutual-funds/other-funds/hdfc-gold-fund (Factsheet)
  10. https://www.hdfcfund.com/mutual-funds/other-funds/hdfc-silver-etf-fund-of-funds (Factsheet)

  **C. HDFC AMC – SID / KIM / SAI (3)**
  11. https://www.hdfcfund.com/statutory-information/scheme-information-documents (SID)
  12. https://www.hdfcfund.com/statutory-information/key-information-memorandum (KIM)
  13. https://www.hdfcfund.com/statutory-information/statement-of-additional-information (SAI)

  **D. HDFC AMC – FAQ / Help / Downloads (3)**
  14. https://www.hdfcfund.com/knowledge-center/faq
  15. https://www.hdfcfund.com/investor-services/account-statements
  16. https://www.hdfcfund.com/investor-services/capital-gains-statement

  **E. AMFI / SEBI – Regulatory & Guidance (4)**
  17. https://www.amfiindia.com/investor-corner/knowledge-center/what-are-mutual-funds.html
  18. https://www.amfiindia.com/investor-corner/knowledge-center/riskometer.html
  19. https://www.sebi.gov.in/legal/regulations/jul-2023/sebi-mutual-funds-regulations-1996-last-amended-on-july-04-2023-_74404.html
  20. https://www.amfiindia.com/nav-history-download

### 2. FAQ Assistant Requirements

The assistant must answer **facts-only queries**, such as:

- Expense ratio of a scheme
- Exit load details
- Minimum SIP amount
- ELSS lock-in period
- Riskometer classification
- Benchmark index
- Process to download statements or capital gains reports

**Response rules:**

- Each response is limited to a **maximum of 3 sentences**
- Each response includes **exactly one citation link**
- Each response includes a footer:

  > "Last updated from sources: \<date\>"

### 3. Refusal Handling

The assistant must refuse non-factual or advisory queries, such as:

- *"Should I invest in this fund?"*
- *"Which fund is better?"*

Refusal responses should:

- Be polite and clearly worded
- Reinforce the facts-only limitation
- Provide a relevant educational link (e.g., AMFI or SEBI resource)

### 4. User Interface (Minimal)

The solution should include a simple interface with:

- A welcome message
- Three example questions
- A visible disclaimer:

  > "Facts-only. No investment advice."

---

## Constraints

### Data and Sources

- Use **only official public sources** (AMC, AMFI, SEBI)
- Do **not** use third-party blogs or aggregator websites

### Privacy and Security

The system must **not** collect, store, or process any of the following:

- PAN or Aadhaar numbers
- Account numbers
- OTPs
- Email addresses or phone numbers

### Content Restrictions

- No investment advice or recommendations
- No performance comparisons or return calculations
- For performance-related queries, provide a link to the official factsheet only

### Transparency

- Responses must be short, factual, and verifiable
- Every answer must include a **source link** and **last updated date**

---

## Expected Deliverables

### README Document

- Setup instructions
- Selected AMC and schemes
- Architecture overview (RAG approach)
- Known limitations

### Disclaimer Snippet

> "Facts-only. No investment advice."

---

## Success Criteria

| # | Criterion |
|---|-----------|
| 1 | Accurate retrieval of factual mutual fund information |
| 2 | Strict adherence to facts-only responses |
| 3 | Consistent inclusion of valid source citations |
| 4 | Proper refusal of advisory queries |
| 5 | Clean, minimal, and user-friendly interface |

---

## Summary

The goal is to build a **trustworthy, transparent, and compliant** mutual fund FAQ assistant that prioritizes **accuracy over intelligence**. The system should ensure that users receive only verified, source-backed financial information, without any advisory bias or speculative content.

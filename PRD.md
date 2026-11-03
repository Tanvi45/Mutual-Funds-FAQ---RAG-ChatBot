# Product Requirements Document (PRD)

**Project Name:** Groww Mutual Fund FAQ RAG Assistant  
**Purpose:** Build a small, fact-only FAQ assistant for HDFC Mutual Fund schemes using official public sources via a Retrieval-Augmented Generation (RAG) pipeline.  
**Target Audience:** Retail users comparing schemes, support/content teams answering repetitive mutual fund questions  
**Constraints:** Public sources only, no PII, no performance/advice, facts-only with citations  

---

## 1. Objective

Create a working prototype of a factual FAQ assistant that answers questions about mutual fund schemes using only official public pages from Groww (AMC and scheme pages). Every answer must include a source link and must strictly avoid investment advice.

---

## 2. Scope

### 2.1 Data Sources (to be scraped/stored)
| # | Source | URL |
|---|--------|-----|
| 1 | AMC Overview - HDFC Mutual Fund | https://groww.in/mutual-funds/amc/hdfc-mutual-funds |
| 2 | Large Cap - HDFC Large Cap Fund Direct Growth | https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth |
| 3 | Flexi Cap - HDFC Flexi Cap Direct Plan Growth | https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth |
| 4 | ELSS (Tax Saver) - HDFC ELSS Tax Saver Fund Direct Plan Growth | https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth |
| 5 | Mid Cap - HDFC Mid Cap Fund Direct Growth | https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth |

### 2.2 Supported Question Types
The assistant should answer factual queries only, including:
- Expense ratio
- Exit load
- Minimum SIP
- Lock-in (ELSS)
- Riskometer
- Benchmark
- How to download statements (e.g., capital gains statement)

### 2.3 Out of Scope
- Investment advice (buy/sell/recommendations/portfolio suggestions)
- Performance claims or return calculations/comparisons
- PII collection/storage (PAN, Aadhaar, account numbers, OTPs, emails, phone numbers)
- Third-party blogs or non-official sources
- App backend screenshots

---

## 3. Functional Requirements

### 3.1 FAQ Assistant Behavior
- **Facts-only responses:** Only answer questions that can be answered from retrieved factual content. 
- **Mandatory citations:** Every answer must include exactly one clear source link.
- **Polite refusals:** For opinionated/portfolio questions (e.g., "Should I buy/sell?"), refuse politely with a facts-only message and a relevant educational link.
- **Concise answers:** Keep answers ≤ 3 sentences.
- **Transparency:** Append "Last updated from sources: " to responses (with appropriate timestamp/date of retrieval/update).
- **No performance claims:** If asked about returns/comparisons, link to the official factsheet instead of computing values.
- **UI Requirements:** Tiny UI with welcome line, 3 example questions, and note: "Facts-only. No investment advice."

### 3.2 RAG Pipeline (Phase-wise Implementation)

This project is a RAG demo; each stage's data must be explicitly stored for demonstration purposes.

#### Phase 1: Data Loading
- Scrape the 5 specified pages (public only).
- Store raw scraped content explicitly (e.g., raw HTML/text files) for inspection.
- Track source URLs for citation purposes.

#### Phase 2: Data Chunking
- Apply a chunking strategy based on the structure of the scraped data (agent to decide optimal strategy - e.g., semantic/section-based/recursive).
- Store chunked data explicitly (e.g., JSON/structured files) with metadata (source URL, section, chunk id).

#### Phase 3: Data Embedding
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2`
- Generate embeddings for all chunks.
- Store embeddings explicitly (linked to chunks/metadata) for demonstration.

#### Phase 4: Vector DB
- **Vector Database:** ChromaDB
- Index chunks with embeddings and metadata.
- All configuration (embedding model, vector DB, paths) must be defined in a configurable `config` file so they can be changed easily.

#### Phase 5: Data Retrieval
- **Embedding Model (Retrieval):** Same as ingestion (`sentence-transformers/all-MiniLM-L6-v2`)
- **Vector DB (Retrieval):** Same as ingestion (ChromaDB)
- Retrieve relevant chunks based on query similarity.

#### Phase 6: LLM Generation
- **Supported Providers:** Groq, Gemini, OpenAI, Anthropic, Mistral (configurable)
- **Primary/Default Model:** `qwen/qwen3-8-27b` (via Groq as primary option)
- API keys must be loaded from `.env` file
- Model selection should be configurable via config/env

---

## 4. Non-Functional Requirements

- **Security/Privacy:** No PII accepted or stored.
- **Source Integrity:** Only official/public pages. Prefer AMC/SEBI/AMFI pages as sources.
- **Configurability:** Central config file for models, DB, chunking strategy parameters.
- **Transparency:** All pipeline stages must have explicit stored artifacts to demonstrate RAG flow.
- **Simplicity:** Tiny UI, concise answers (≤3 sentences).
- **Extensibility:** Support multiple LLM providers via configuration.

---

## 5. Deliverables

| Deliverable | Description |
|-------------|-------------|
| Working Prototype | App/Notebook link, or ≤3-min demo video if hosting not possible |
| Source List | CSV/MD with 15–25 URLs used |
| README | Setup steps, scope (AMC + schemes), known limits |
| Sample Q&A File | 5–10 queries with assistant answers + source links |
| Disclaimer Snippet | Used in UI (facts-only, no advice) |

---

## 6. Skills Being Tested

| Skill | Focus |
|-------|-------|
| W1 - Thinking Like a Model | Identify exact fact asked; decide answer vs. refuse |
| W2 - LLMs & Prompting | Instruction style, concise phrasing, polite safe-refusals, citation wording |
| W3 - RAGs (only) | Small-corpus retrieval with accurate citations from AMC/SEBI/AMFI pages |

---

## 7. Technical Design Notes

### Configuration
Create a configuration module/file (e.g., `config.yaml`/`config.py`) with:
- `data_loading`: source URLs, storage paths
- `chunking`: strategy name/parameters (to be decided by agent based on data)
- `embedding`: model name (`sentence-transformers/all-MiniLM-L6-v2`)
- `vector_db`: type (`chromadb`), persist path, collection name
- `retrieval`: top-k, similarity threshold
- `llm`: provider (`groq` default), model (`qwen/qwen3.8-27b`), API key env var names, support for gemini/openai/anthropic/mistral

### Environment Variables
Store secrets in `.env`:
- `GROQ_API_KEY` (and optionally others for Gemini/OpenAI/Anthropic/Mistral)
- `LLM_MODEL` (e.g., `qwen/qwen3.8-27b`)
- Provider-specific keys as needed

### Data Artifacts (for demo)
Explicitly persist at each stage:
- `data/raw/` - scraped raw content
- `data/chunks/` - chunked data with metadata
- `data/embeddings/` - embedding artifacts/index references
- `chroma/` or configured persist dir - vector store

---

## 8. Acceptance Criteria

- [ ] All 5 sources scraped and stored explicitly
- [ ] Pipeline implemented phase-wise with artifacts stored at each stage
- [ ] Embedding uses `sentence-transformers/all-MiniLM-L6-v2` for both ingestion and retrieval
- [ ] ChromaDB used as vector store with config-driven setup
- [ ] Config file created for all changeable components (chunking, models, DB)
- [ ] LLM integration supports Groq with `qwen/qwen3.8-27b` from `.env` and structure for other providers
- [ ] Every answer includes exactly one source link
- [ ] Refuses opinionated questions politely with educational link
- [ ] Answers ≤ 3 sentences, includes "Last updated from sources: "
- [ ] No PII handling, no advice/performance claims
- [ ] UI has welcome line, 3 examples, disclaimer note
- [ ] All 5 deliverables prepared

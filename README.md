# FAQ Assistant – Mutual Fund RAG Chatbot

A Streamlit-based Retrieval-Augmented Generation (RAG) chatbot that answers factual questions about selected HDFC Mutual Fund schemes using information retrieved from a curated knowledge base.

The assistant is designed for factual information retrieval. It is not an investment adviser and does not provide personalised investment recommendations.

## Features

- Answers factual questions about selected HDFC Mutual Fund schemes.
- Uses semantic search to retrieve relevant text from a ChromaDB vector database.
- Generates query embeddings with Sentence Transformers.
- Applies a similarity threshold to filter retrieved chunks.
- Uses Groq for concise answers grounded in retrieved source excerpts.
- Displays source references so users can inspect the supporting material.
- Includes a Streamlit interface with fund-selection cards, chat, and related questions.
- Communicates its scope and facts-only limitation to users.

## Knowledge-base scope

The current knowledge base is focused on HDFC Mutual Fund information, including the following scheme areas:

- HDFC Large Cap Fund
- HDFC Flexi Cap Fund
- HDFC ELSS Tax Saver Fund
- HDFC Mid Cap Fund
- HDFC Mutual Fund AMC information

The indexed data includes source information and URLs as metadata. The assistant can only answer from information available in its indexed sources. If the retrieved excerpts do not support an answer, it is designed to say that the information is not available in the indexed sources.

**Source limitation:** The current app has historically used selected Groww mutual-fund pages and an AMFI reference in its prepared data. Check the source register and the indexed data before describing the knowledge base as exclusively official AMC, SEBI, or AMFI material. A candidate source list is not proof that every listed URL has been scraped or indexed.

## Tech stack

- Python
- Streamlit
- ChromaDB
- Sentence Transformers (`sentence-transformers/all-MiniLM-L6-v2`)
- Groq API
- Retrieval-Augmented Generation (RAG)

## Project structure

```text
Build Hour- RAG/
├── src/
│   ├── app.py                 # Streamlit application
│   ├── data_loader.py         # Source-page collection
│   ├── document_loader.py     # Document loading
│   ├── chunker.py             # Text chunking
│   ├── embedder.py            # Embedding generation
│   ├── vector_store.py        # ChromaDB indexing
│   ├── retriever.py           # Semantic retrieval
│   └── generator.py           # Grounded Groq answer generation
├── data/
│   ├── chunks/
│   │   └── chunks.json
│   ├── embeddings/
│   │   └── embeddings.json
│   └── source_list.csv        # Source register, if present
├── chroma/                    # Persistent ChromaDB data (created/used locally)
├── rag/                       # Separate pipeline scaffold
├── scripts/
├── config.yaml
├── requirements.txt
├── .env                       # Local secrets; do not commit
└── README.md
```

The Streamlit application runs from `src/app.py` and uses the `src` modules for vector storage, retrieval, and answer generation. The separate `rag/` directory is a newer pipeline scaffold; it should not be assumed to be the execution path of the current Streamlit app.

## Prerequisites

- Python version compatible with the packages in `requirements.txt`
- A Groq API key
- Internet access for Groq API requests and any remote resources used by the app

## Setup and run locally

### 1. Clone the repository

```bash
git clone https://github.com/Tanvi45/Mutual-Funds-FAQ---RAG-ChatBot.git
cd Mutual-Funds-FAQ---RAG-ChatBot
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
```

If PowerShell blocks activation, you can run the environment's Python executable directly as shown in the run step below.

### 3. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Configure the Groq API key

Create a local `.env` file in the project root. Add your own key:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

Optionally, set `LLM_MODEL` to a Groq-supported model available to your account:

```dotenv
LLM_MODEL=your_model_name
```

Do not share your `.env` file or commit it to GitHub. Keep `.env` excluded through `.gitignore`.

### 5. Run the Streamlit app

```powershell
.\.venv\Scripts\python.exe -m streamlit run src/app.py
```

Streamlit will print a local URL, normally:

```text
http://localhost:8501
```

Open that URL in your browser.

## How the RAG workflow works

1. **Source collection:** selected source pages are collected for the knowledge base.
2. **Document loading:** source content is loaded into a consistent document format.
3. **Chunking:** documents are divided into smaller text sections.
4. **Embedding:** the Sentence Transformers model converts chunks into numerical vectors.
5. **Vector storage:** chunk text, embeddings, IDs, and source metadata are stored in ChromaDB.
6. **Retrieval:** the user's question is embedded and compared with stored vectors using cosine distance.
7. **Generation:** retrieved excerpts are passed to Groq to produce a concise, source-grounded response.
8. **Source display:** source references are shown with the answer so users can inspect the supporting material.

The live app uses the persistent ChromaDB collection `hdfc_mf_faq` in the `./chroma` directory. If the collection is empty, the app indexes the prepared `data/embeddings/embeddings.json` file.

## Safety and limitations

- Facts-only information assistant; not financial or investment advice.
- Does not provide personalised investment recommendations.
- Does not make unsupported fund comparisons or performance claims.
- Answers are limited by the content and freshness of the indexed sources.
- If the retrieved evidence does not directly support an answer, the assistant should state that the information is unavailable in the indexed sources.
- Source URLs and displayed source references should be checked against the underlying source register and indexed records.
- This is an independent project and is not affiliated with HDFC Mutual Fund or Groww.

## Data and refresh notes

The prepared chunk and embedding JSON files are used to populate the ChromaDB collection. When the collection already contains records, the app uses that existing collection rather than automatically rebuilding it on every launch.

To refresh the knowledge base, update and validate the source data and prepared embeddings using the project's ingestion workflow, then deliberately re-index the intended data. Back up the existing data before performing a refresh.

## Disclaimer

This assistant provides general factual information from its indexed sources only. It does not provide investment advice, personalised recommendations, or a substitute for official scheme documents. Verify important details with the relevant AMC, AMFI, or SEBI material before making financial decisions.

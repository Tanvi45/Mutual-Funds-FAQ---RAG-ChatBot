# HDFC Mutual Funds FAQ – RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that answers user questions about HDFC Mutual Fund schemes using information retrieved from a curated FAQ knowledge base.

## Features
- Answers questions related to HDFC Mutual Fund schemes.
- Retrieves relevant information from a Chroma vector database.
- Uses sentence-transformer embeddings for semantic search.
- Applies reranking to improve the relevance of retrieved context.
- Generates responses using the Groq LLM.
- Built with Streamlit for an interactive chat interface.

## Tech Stack
- Python
- Streamlit
- Groq API
- ChromaDB
- Sentence Transformers
- Retrieval-Augmented Generation (RAG)

## Run Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/Tanvi45/Mutual-Funds-FAQ---RAG-ChatBot.git
   cd Mutual-Funds-FAQ---RAG-ChatBot
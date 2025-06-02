# Chatbot - Medical Assistant

## Features
- [x] Chat session management
- [x] Local file management
- [x] Q&A with documents
- [x] Support PDF and TXT files

## Run

1. Retrieve Gemini API Key here: https://ai.google.dev/gemini-api/docs/api-key

1. Copy a file `.env` from `.env.docker` and update the API key:

    ```
    GEMINI_API_KEY=<ADD YOUR API KEY HERE>
    ```

1. Pull docker images and start

    ```
    docker compose up -d
    ```

1. (Optional) To view logs, run:

    ```
    docker compose logs -f
    ```

1. Navigate to: http://localhost:8000

## Development

1. Install [`uv`](https://docs.astral.sh/uv/)
1. Install dependencies

    ```
    uv sync --locked
    ```

1. Retrieve Gemini API Key here: https://ai.google.dev/gemini-api/docs/api-key

1. Update environment variables from [.env.host](.env.host)

    ```
    GEMINI_API_KEY=<ADD YOUR API KEY HERE>
    ```

1. Rename the file to `.env`

1. Execute commands:

    ```
    PYTHONPATH=apps uv run streamlit run apps/web/main.py --server.runOnSave=True
    ```

1. Open browser at (usually): http://localhost:8051

## Architecture

### Stack

- App: Streamlit
- LLM Provider: Gemini 2.5 Flash
- Text Embedding: Gemini Embedding
- LLM Framework: Agno
- Vector Database: Weaviate
- Storage Database: SQLite

### Workflow

This application is separated into two phases:
1. Document management
2. Chat Q&A

Phase 1: Document management
1. User upload documents (pdf, txt supported)
1. Document is then processed and chunked and embedded into vector with Gemini Embedding model
1. Vector is saved into Weaviate with its metadata such as file location, textual content, etc.

Phase 2: Document retrieval
1. User ask question (query)
1. Agent will compare the query embedding, using Gemini Embedding, with vectors stored in Weaviate to retrieve relevant documents
1. Top-5 documents are retrieved
1. (Optional) Re-ranking documents with its relevancy - Not Yet Implemented
1. Embed the document contents to the prompt and let the LLM model cooks.

## References

- Agno Agentic RAG: https://github.com/agno-agi/agno/tree/main/cookbook/examples/streamlit_apps/agentic_rag
- Gemini API: https://ai.google.dev/gemini-api/docs
- Sample PDF file: https://lab.mlaw.gov.sg/files/Sample-filled-in-MR.pdf

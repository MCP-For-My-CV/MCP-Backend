# MCP Server - Document Ingestion System

A Python-based document ingestion system that processes PDF files and stores them in a vector database for semantic search capabilities.

## Features

- **PDF Processing**: Automatically processes PDF files from a designated folder
- **Vector Storage**: Uses ChromaDB with HuggingFace embeddings for document storage
- **Multiple Model Support**: Supports Ollama and Grok language models
- **Automatic File Processing**: Monitors a folder and processes new files automatically
- **Semantic Search**: Query documents using natural language

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.template` to `.env` and configure your API keys:

```bash
cp .env.template .env
```

Edit `.env` and add your API keys:

```
XAI_API_KEY=your_grok_api_key_here  # Optional, only needed for Grok model
```

### 3. Folder Structure

The system expects the following folder structure:

```
MCP Server/
├── Data/          # Place PDF files here for processing
├── DB/            # Vector database storage (auto-created)
├── ingest.py      # Main ingestion script
├── models.py      # Model configurations
└── test_ingest.py # Test script
```

## Usage

### Manual File Processing

To process a single PDF file:

```python
from ingest import ingest_file
ingest_file('./Data/your_document.pdf')
```

### Automatic Folder Monitoring

To continuously monitor the `Data` folder for new PDF files:

```bash
python ingest.py
```

This will:

1. Monitor the `./Data` folder every 10 seconds
2. Process any PDF files that don't start with `_`
3. Add a `_` prefix to processed files to avoid reprocessing
4. Store document chunks in the ChromaDB vector database

### Testing the System

Run the test script to verify everything works:

```bash
python test_ingest.py
```

### Querying Documents

```python
from ingest import vector_store

# Search for similar content
results = vector_store.similarity_search("your query here", k=3)

for doc in results:
    print(doc.page_content)
```

## Configuration

### Document Processing Settings

In `ingest.py`, you can modify:

- `chunks_size`: Size of text chunks (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 50)
- `check_interval`: Folder monitoring interval in seconds (default: 10)

### Model Selection

The system supports multiple embedding and language models:

#### Embeddings:

- **HuggingFace** (default): `sentence-transformers/all-MiniLM-L6-v2`
- **Ollama**: `mxbai-embed-large` (requires Ollama running locally)

#### Language Models:

- **Ollama**: `llama3.2` (requires Ollama running locally)
- **Grok**: `grok-4-latest` (requires XAI_API_KEY)

## Dependencies

Key packages:

- `langchain-chroma`: Vector database
- `langchain-community`: Document loaders
- `langchain-huggingface`: HuggingFace embeddings
- `langchain-ollama`: Ollama integration
- `pypdf`: PDF processing
- `sentence-transformers`: Embedding models

## Troubleshooting

### Ollama Connection Issues

If you see "Failed to connect to Ollama" errors:

1. Install Ollama from https://ollama.com/download
2. Start Ollama service
3. Pull required models: `ollama pull llama3.2` and `ollama pull mxbai-embed-large`

The system will automatically fall back to HuggingFace embeddings if Ollama is not available.

### Memory Issues

For large documents, you may need to:

- Reduce `chunks_size` in `ingest.py`
- Process files individually rather than using the monitoring loop

## File Processing

- Only PDF files are processed
- Files starting with `_` are ignored (considered already processed)
- Processed files are automatically renamed with a `_` prefix
- The system creates document chunks with metadata including page numbers and source file information

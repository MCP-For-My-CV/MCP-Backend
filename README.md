# MCP Server - CV RAG System

A Python-based Retrieval Augmented Generation (RAG) system that processes PDF files and allows question answering using a REST API.

## Features

- **PDF Processing**: Automatically processes PDF files from a designated folder
- **Vector Storage**: Uses ChromaDB with OpenAI/HuggingFace embeddings
- **Multiple Model Support**: Supports OpenAI and Ollama language models
- **REST API**: Provides HTTP endpoints for interacting with the system
- **MCP Server**: Implements the Model Context Protocol for tool integration
- **Docker Support**: Easy deployment with Docker

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file and configure your API keys:

```
OPENAI_API_KEY=your_openai_api_key_here
EMAIL_PASSWORD=your_email_password_here  # Optional, for email functionality
```

### 3. Folder Structure

The system expects the following folder structure:

```
MCP-Backend/
├── Data/          # Place PDF files here for processing
├── DB/            # Vector database storage (auto-created)
├── ingest.py      # Main ingestion script
├── models.py      # Model configurations
├── chat.py        # Chat interface for querying
├── mcp_server.py  # MCP server implementation
├── rest_api.py    # REST API server
└── rag_core.py    # RAG core functionality
```

## Usage

### Running the REST API Server

```bash
python rest_api.py
```

This will:

1. Start the FastAPI server on port 8000
2. Initialize the RAG system with models and vector store
3. Provide endpoints for RAG and email functionality

### Running the MCP Server

```bash
python mcp_server.py
```

### Ingesting Documents

```bash
python ingest.py
```

This will:

1. Process any PDF files in the `./Data` folder
2. Add a `_` prefix to processed files to avoid reprocessing
3. Store document chunks in the ChromaDB vector database

### Querying Documents

You can use the interactive chat interface:

```bash
python chat.py
```

Or query directly through the REST API:

```bash
curl -X POST "http://localhost:8000/tools/rag" \
     -H "Content-Type: application/json" \
     -d '{"question": "What skills do I have?"}'
```

### CORS Configuration

The REST API has CORS enabled to allow frontend applications to access it. You can configure CORS using environment variables:

```bash
# Allow all origins (default)
export CORS_ORIGINS="*"

# Allow specific origins
export CORS_ORIGINS="https://example.com,https://app.example.com"
```

## Docker Deployment

### Building and Running with Docker

1. Build the Docker image:

```bash
docker build -t mcp-cv-rag .
```

2. Run the container:

```bash
docker run -p 8000:8000 -e OPENAI_API_KEY=your_openai_api_key mcp-cv-rag
```

Or use the provided scripts:

```bash
# Linux/Mac
./docker-run.sh

# Windows
./docker-run.ps1
```

### Deploying to Render

1. Push your repository to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Set the following:
   - Environment: Docker
   - Environment Variables: Add your `OPENAI_API_KEY`

## API Endpoints

### RAG Endpoint

```
POST /tools/rag
```

Request body:

```json
{
  "question": "What skills do I have?"
}
```

Response:

```json
{
  "question": "What skills do I have?",
  "answer": "Your skills include Python, JavaScript, Angular, .NET, SQL, and data analysis.",
  "timestamp": "2025-09-04 13:37:14",
  "status": "success"
}
```

### Email Endpoint

```
POST /tools/email
```

Request body:

```json
{
  "recipient": "example@example.com",
  "subject": "Test Email",
  "body": "This is a test email"
}
```

## Configuration

### Model Settings

In `models.py`, you can configure which models to use for:

- Embeddings (OpenAI, Ollama, HuggingFace)
- Language models (OpenAI, Ollama)

### Document Processing Settings

In `ingest.py`, you can modify:

- `chunks_size`: Size of text chunks (default: 1000)
- `chunks_overlap`: Overlap between chunks (default: 200)

## Dependencies

Key packages:

- `langchain-chroma`: Vector database
- `langchain-community`: Document loaders
- `langchain-openai`: OpenAI integration
- `langchain-huggingface`: HuggingFace embeddings
- `langchain-ollama`: Ollama integration
- `pypdf`: PDF processing
- `fastapi`: REST API framework
- `uvicorn`: ASGI server
- `mcp`: Model Context Protocol
- `sentence-transformers`: Embedding models (fallback)

## Troubleshooting

### Ollama Connection Issues

If you see "Failed to connect to Ollama" errors:

1. Install Ollama from https://ollama.com/download
2. Start Ollama service
3. Pull required models: `ollama pull llama3.2` and `ollama pull mxbai-embed-large`

The system will automatically use OpenAI models if Ollama is not available.

### Memory Issues

For large documents, you may need to:

- Reduce `chunks_size` in `ingest.py`
- Process files individually rather than using the monitoring loop

## File Processing

- Only PDF files are processed
- Files starting with `_` are ignored (considered already processed)
- Processed files are automatically renamed with a `_` prefix
- The system creates document chunks with metadata including page numbers and source file information

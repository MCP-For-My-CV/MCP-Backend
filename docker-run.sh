#!/bin/bash
# Build and run the Docker container

# Build the Docker image
docker build -t mcp-cv-rag .

# Run the container
docker run -p 8000:8000 -e OPENAI_API_KEY=$OPENAI_API_KEY mcp-cv-rag

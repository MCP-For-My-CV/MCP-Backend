#!/usr/bin/env python3
"""
REST API wrapper for MCP Server
This creates REST endpoints that call the MCP tools
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
from mcp_server import rag, send_email
from rag_core import initialize_rag

app = FastAPI(
    title="MCP CV RAG Server API",
    description="REST API wrapper for MCP Server tools",
    version="1.0.0"
)

# Request models
class RAGRequest(BaseModel):
    question: str

class EmailRequest(BaseModel):
    recipient: str
    subject: str
    body: str

# Response models
class RAGResponse(BaseModel):
    question: str
    answer: str
    timestamp: str
    status: str = "success"

class EmailResponse(BaseModel):
    result: str

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "MCP CV RAG Server API",
        "status": "running",
        "endpoints": {
            "rag": "POST /tools/rag",
            "email": "POST /tools/email",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "MCP CV RAG Server"}

# RAG endpoint
@app.post("/tools/rag", response_model=RAGResponse)
async def rag_endpoint(request: RAGRequest):
    """Ask a question to the RAG system"""
    try:
        from datetime import datetime
        
        # Get the answer from the RAG system
        answer = rag(request.question)
        
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return RAGResponse(
            question=request.question, 
            answer=answer,
            timestamp=timestamp
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Email endpoint
@app.post("/tools/email", response_model=EmailResponse)
async def email_endpoint(request: EmailRequest):
    """Send an email"""
    try:
        result = send_email(request.recipient, request.subject, request.body)
        return EmailResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    print(f"[SERVER] Starting REST API Server on http://localhost:{port}")
    print(f"[DOCS] API Documentation: http://localhost:{port}/docs")
    print(f"[RAG] RAG Endpoint: POST http://localhost:{port}/tools/rag")
    print(f"[EMAIL] Email Endpoint: POST http://localhost:{port}/tools/email")
    
    # Initialize RAG system at startup
    print("[INFO] Initializing RAG system...")
    initialize_rag()
    print("[SUCCESS] RAG system initialization complete")
    
    uvicorn.run(app, host="0.0.0.0", port=port)

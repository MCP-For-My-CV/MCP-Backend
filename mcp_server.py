from mcp.server import FastMCP
import os
import sys
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from rag_core import initialize_rag, query_rag
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from datetime import datetime
import threading

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("CV RAG Server - Streamable")

# Initialize FastAPI app
app = FastAPI(
    title="MCP CV RAG Server API",
    description="REST API for MCP Server tools",
    version="1.0.0"
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "*").split(",")
if len(origins) == 1 and origins[0] == "*":
    # Allow all origins mode
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    print(f"[CORS] Allowing requests from all origins")
else:
    # Restricted origins mode
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
    print(f"[CORS] Allowing requests from: {', '.join(origins)}")

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

# -------- RAG Tool -------- #
@mcp.tool()
def rag(question: str) -> str:
    """
    Ask a question to the RAG system and get an answer based on CV content.
    
    Args:
        question: Your question about the CV/resume
        
    Returns:
        AI-generated answer based on the CV content
    """
    try:
        answer = query_rag(question)
        return answer
    except Exception as e:
        return f"[ERROR] RAG system error: {str(e)}"

# -------- Email Tool -------- #
@mcp.tool()
def send_email(recipient: str, subject: str, body: str) -> str:
    """
    Send an email to a specified recipient.
    
    Args:
        recipient: Email address of the recipient
        subject: Email subject line
        body: Email message body
        
    Returns:
        Success message or error details
    """
    try:
        sender = os.getenv("EMAIL_USER", "your.email@gmail.com")
        password = os.getenv("EMAIL_PASSWORD")

        if not password:
            return "[ERROR] EMAIL_PASSWORD not set in environment variables"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, [recipient], msg.as_string())

        return f"✅ Email sent successfully to {recipient}"
    except Exception as e:
        return f"[ERROR] Failed to send email: {str(e)}"

# -------- System Info Tool -------- #
@mcp.tool()
def get_server_info() -> str:
    """
    Get information about the MCP server and its capabilities.
    
    Returns:
        Server information and available tools
    """
    return """
    🤖 CV RAG MCP Server - Streamable Version
    
    Available Tools:
    • rag(question) - Ask questions about CV content
    • send_email(recipient, subject, body) - Send emails
    • get_server_info() - Get this information
    
    Server Features:
    • Remote HTTP/WebSocket access
    • OpenAI-powered responses
    • Memory-optimized for cloud deployment
    
    Status: Online and ready to serve requests
    """

# -------- REST API Endpoints -------- #

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

# -------- Run Streamable MCP Server -------- #
if __name__ == "__main__":
    import logging
    
    # Load environment variables
    load_dotenv()
    
    # Initialize RAG system at startup
    print("🔄 Initializing RAG system...")
    try:
        initialize_rag()
        print("✅ RAG system initialized successfully")
    except Exception as e:
        print(f"❌ RAG initialization failed: {e}")
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Starting Unified MCP+HTTP Server...")
    print(f"📍 Environment: {'Production' if os.getenv('RENDER') else 'Development'}")
    print(f"🔑 OpenAI API Key: {'✅ Configured' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"📧 Email: {'✅ Configured' if os.getenv('EMAIL_PASSWORD') else '❌ Missing'}")
    
    # Configure server settings
    mcp_port = int(os.getenv('MCP_PORT', 8001))  # Default to 8001 for MCP
    http_port = int(os.getenv('PORT', 8000))     # Default to 8000 for HTTP
    
    print(f"🌐 Servers will be accessible at:")
    print(f"   • HTTP API: http://localhost:{http_port}")
    print(f"   • HTTP API Docs: http://localhost:{http_port}/docs")
    print(f"   • MCP: stdio transport")
    print()
    
    # Start HTTP server in a separate thread
    def start_http_server():
        try:
            uvicorn.run(app, host="0.0.0.0", port=http_port)
        except Exception as e:
            print(f"❌ HTTP Server error: {e}")
    
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    print(f"✅ HTTP server started on port {http_port}")
    
    try:
        # Run the MCP server
        print(f"✅ Starting MCP server")
        mcp.run()
    except KeyboardInterrupt:
        print("\n🛑 Servers stopped by user")
    except Exception as e:
        print(f"❌ MCP Server error: {e}")
        sys.exit(1)

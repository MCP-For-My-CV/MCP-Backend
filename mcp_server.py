from mcp.server import FastMCP
import subprocess
import smtplib
from email.mime.text import MIMEText
import os
import sys
from rag_core import initialize_rag, query_rag

# Initialize FastMCP server
mcp = FastMCP("CV RAG Server")

# -------- RAG Tool -------- #
@mcp.tool()
def rag(question: str) -> str:
    """
    Ask a question to the RAG system and get an answer.
    """
    try:
        # Use the reusable RAG function instead of running as subprocess
        answer = query_rag(question)
        return answer
    except Exception as e:
        return f"[ERROR] Exception running RAG system: {str(e)}"


# -------- Email Tool -------- #
@mcp.tool()
def send_email(recipient: str, subject: str, body: str) -> str:
    """
    Send an email to the specified recipient.
    """
    try:
        sender = os.getenv("EMAIL_USER", "wimukthimadushan6@gmail.com")
        password = os.getenv("EMAIL_PASSWORD")  # load from env variable

        if not password:
            return "[ERROR] EMAIL_PASSWORD not set in environment"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, [recipient], msg.as_string())

        return f"✅ Email sent to {recipient}"
    except Exception as e:
        return f"[ERROR] Failed to send email: {str(e)}"


# -------- Run MCP Server -------- #
if __name__ == "__main__":
    import logging
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Set up logging for deployment
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Starting MCP Server...")
    print(f"📍 Environment: {'Production' if os.getenv('RENDER') else 'Development'}")
    print(f"OpenAI API Key: {'[CONFIGURED]' if os.getenv('OPENAI_API_KEY') else '[MISSING]'}")
    
    # Always use HTTP transport with URL
    port = int(os.getenv('PORT', 8001))  # Default to port 8001
    host = '0.0.0.0' if os.getenv('RENDER') else '127.0.0.1'
    
    print(f"🌐 Starting MCP Server with HTTP transport")
    print(f"📡 Server URL: http://{host}:{port}")
    print(f"🔗 Local access: http://localhost:{port}")
    print(f"� MCP clients can connect via HTTP transport")
    
    try:
        # Always run with HTTP transport
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        print("🛑 Server stopped by user")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")
        if not os.getenv('RENDER'):
            raise

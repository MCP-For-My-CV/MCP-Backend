from mcp.server import FastMCP
import subprocess
import smtplib
from email.mime.text import MIMEText
import os
import sys

# Initialize FastMCP server
mcp = FastMCP("CV RAG Server")

# -------- RAG Tool -------- #
@mcp.tool()
def rag(question: str) -> str:
    """
    Ask a question to the RAG system and get an answer.
    """
    try:
        result = subprocess.run(
            [sys.executable, "chat.py", question],   # use current python interpreter
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)           # run inside project folder
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"❌ RAG Error: {result.stderr.strip()}"
    except Exception as e:
        return f"❌ Exception running RAG system: {str(e)}"


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
            return "❌ EMAIL_PASSWORD not set in environment"

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
        return f"❌ Failed to send email: {str(e)}"


# -------- Run MCP Server -------- #
if __name__ == "__main__":
    print("🚀 Starting MCP Server...")
    mcp.run()

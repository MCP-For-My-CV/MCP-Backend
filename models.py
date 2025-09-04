import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load environment variables
load_dotenv()


class Models:
    def __init__(self):
        # Flag to check if we should only use OpenAI embeddings (for Render deployment)
        self.openai_embeddings_only = os.getenv("OPENAI_EMBEDDINGS_ONLY", "false").lower() == "true"
        
        # Initialize OpenAI models using provided API key
        openai_api_key = os.getenv("OPENAI_API_KEY") 
        if openai_api_key:
            try:
                self.embeddings_openai = OpenAIEmbeddings(
                    api_key=openai_api_key,
                    model="text-embedding-3-small"
                )
                self.model_openai = ChatOpenAI(
                    api_key=openai_api_key,
                    model="gpt-3.5-turbo",
                    temperature=0.1
                )
                print("[SUCCESS] OpenAI models initialized successfully")
            except Exception as e:
                print(f"[ERROR] OpenAI initialization failed: {e}")
                self.embeddings_openai = None
                self.model_openai = None
        else:
            print("[INFO] No OPENAI_API_KEY found")
            self.embeddings_openai = None
            self.model_openai = None

        # Try Ollama embeddings as backup if not in OpenAI-only mode
        if not self.openai_embeddings_only:
            try:
                # Quick test to see if Ollama is available
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    self.embeddings_ollama = OllamaEmbeddings(
                        model="mxbai-embed-large"
                    )
                    print("[SUCCESS] Ollama embeddings initialized successfully")
                else:
                    raise Exception("Ollama server not responding")
            except Exception as e:
                print(f"[INFO] Ollama embeddings not available: {e}")
                self.embeddings_ollama = None
        else:
            print("[INFO] Skipping Ollama embeddings (OPENAI_EMBEDDINGS_ONLY=true)")
            self.embeddings_ollama = None

        # Initialize HuggingFace embeddings only if not in OpenAI-only mode
        if not self.openai_embeddings_only:
            self.embeddings_hf = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            print("[INFO] HuggingFace embeddings initialized")
        else:
            print("[INFO] Skipping HuggingFace embeddings (OPENAI_EMBEDDINGS_ONLY=true)")
            self.embeddings_hf = None

        # Try Ollama chat model as backup if not in OpenAI-only mode
        if not self.openai_embeddings_only:
            try:
                # Quick test to see if Ollama is available
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    self.model_ollama = ChatOllama(
                        model="llama3.2"
                    )
                    print("[SUCCESS] Ollama chat model initialized successfully")
                else:
                    raise Exception("Ollama server not responding")
            except Exception as e:
            print(f"[INFO] Ollama chat model not available: {e}")
            self.model_ollama = None

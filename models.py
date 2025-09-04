import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load environment variables
load_dotenv()


class Models:
    def __init__(self):
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
                
                # Set these to None since we're only using OpenAI
                self.embeddings_ollama = None
                self.model_ollama = None
                self.embeddings_hf = None
                
            except Exception as e:
                print(f"[ERROR] OpenAI initialization failed: {e}")
                self.embeddings_openai = None
                self.model_openai = None
                raise Exception(f"OpenAI initialization failed: {e}")
        else:
            print("[ERROR] No OPENAI_API_KEY found in environment variables")
            raise Exception("No OPENAI_API_KEY found in environment variables")
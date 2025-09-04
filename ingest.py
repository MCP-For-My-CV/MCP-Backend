import os
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from uuid import uuid4
from models import Models

load_dotenv()

# Initialize Models
models = Models()
if models.embeddings_openai:
    embeddings = models.embeddings_openai
    print("Using OpenAI embeddings for ingestion")
elif models.embeddings_ollama:
    embeddings = models.embeddings_ollama
    print("Using Ollama embeddings for ingestion")
else:
    embeddings = models.embeddings_hf
    print("Using HuggingFace embeddings for ingestion")

llm = models.model_openai if models.model_openai else models.model_ollama

data_folder = "./Data"
chunks_size = 1000
chunk_overlap = 50
check_interval = 10

# Chroma vector store
vector_store = Chroma(
    collection_name="documents",
	embedding_function=embeddings,
	persist_directory="./DB/chroma_langchain_db"
)

# Ingest File
def ingest_file(file_path):
    try:
        print(f"Loading document: {file_path}")
        loader = PyPDFLoader(file_path)
        loaded_documents = loader.load()
        
        if not loaded_documents:
            print(f"No content found in {file_path}")
            return
            
        print(f"Splitting {len(loaded_documents)} pages into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunks_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        documents = text_splitter.split_documents(loaded_documents)
        
        print(f"Created {len(documents)} chunks")
        uuids = [str(uuid4()) for _ in range(len(documents))]
        
        print("Adding documents to vector store...")
        vector_store.add_documents(documents=documents, ids=uuids)
        print("Ingestion complete.")
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        raise


def main_loop():
    print(f"Monitoring folder: {data_folder}")
    print("Press Ctrl+C to stop...")
    
    try:
        while True:
            processed_files = False
            
            if not os.path.exists(data_folder):
                print(f"Data folder {data_folder} does not exist. Creating it...")
                os.makedirs(data_folder, exist_ok=True)
            
            for filename in os.listdir(data_folder):
                if filename.endswith(".pdf") and not filename.startswith("_"):  # Only process PDF files
                    file_path = os.path.join(data_folder, filename)
                    print(f"Processing file: {filename}")
                    
                    try:
                        ingest_file(file_path)
                        
                        # Add a prefix to processed file
                        new_filename = "_" + filename
                        new_file_path = os.path.join(data_folder, new_filename) 
                        os.rename(file_path, new_file_path)
                        print(f"File renamed to: {new_filename}")
                        processed_files = True
                        
                    except Exception as e:
                        print(f"Failed to process {filename}: {e}")

            if not processed_files:
                print(f"No new files to process. Waiting {check_interval} seconds...")
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\nStopping file monitor...")
    except Exception as e:
        print(f"Error in main loop: {e}") 

if __name__ == "__main__":
    main_loop()
"""
RAG Core Module
This module initializes the RAG system once and provides a reusable query function
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain 
from langchain_chroma import Chroma
from models import Models

# Global variables to store initialized components
llm = None
retrieval_chain = None
models = None
initialized = False

def initialize_rag():
    """Initialize the RAG system once"""
    global llm, retrieval_chain, models, initialized
    
    if initialized:
        return True
    
    print("[DEBUG] Starting RAG initialization...")
    
    # Initialize The Models (OpenAI only)
    models = Models()
    
    # Use OpenAI embeddings (no fallbacks)
    embeddings = models.embeddings_openai
    llm = models.model_openai
    print("[INFO] Using OpenAI embeddings and chat model")
    
    print("[DEBUG] Initializing vector store...")
    
    # Initialize the vector store
    try:
        vector_store = Chroma(
            collection_name="documents",
            embedding_function=embeddings,
            persist_directory="./DB/chroma_langchain_db"
        )
        print("[DEBUG] Vector store initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize vector store: {e}")
        return False
    
    print("[DEBUG] Setting up retrieval chain...")
    
    # Define the chat prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant. Answer the question based only on the data provided"),
            ("human", "Use the user question {input} to answer the question. Use only the {context} to answer the question.")
        ] 
    )
    
    try:
        # Define the retrieval chain
        retriever = vector_store.as_retriever(search_kwargs={"k":10})
        
        # Create the retrieval chain with the available LLM
        combine_docs_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
        retrieval_chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=combine_docs_chain)
        print("[DEBUG] Retrieval chain created")
    except Exception as e:
        print(f"[ERROR] Failed to create retrieval chain: {e}")
        return False
    
    print("[SUCCESS] Chat system ready!")
    initialized = True
    return True

def query_rag(question):
    """Query the RAG system with a question"""
    global retrieval_chain, initialized
    
    # Make sure the system is initialized
    if not initialized:
        success = initialize_rag()
        if not success:
            return "Failed to initialize RAG system"
    
    try:
        # Process the query through the retrieval chain
        response = retrieval_chain.invoke({"input": question})
        return response["answer"]
    except Exception as e:
        return f"Error processing query: {str(e)}"

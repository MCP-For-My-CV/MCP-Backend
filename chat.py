from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain 
from langchain_chroma import Chroma
from models import Models

#Initialize The Models

models = Models()

if models.embeddings_openai:
    embeddings = models.embeddings_openai
    print("Using OpenAI embeddings for chat")
elif models.embeddings_ollama:
    embeddings = models.embeddings_ollama
    print("Using Ollama embeddings for chat")
else:
    embeddings = models.embeddings_hf
    print("Using HuggingFace embeddings for chat")

# Try to connect to available language models
llm = None
print("Initializing language model...")


# First try OpenAI if API key is available
if models.model_openai:
    try:
        print("Testing OpenAI connection...")
        llm = models.model_openai
        print("✅ Using OpenAI chat model")
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")

# If OpenAI failed or not available, try Ollama
if not llm and models.model_ollama:
    try:
        print("Testing Ollama connection...")
        from langchain_core.messages import HumanMessage
        test_response = models.model_ollama.invoke([HumanMessage(content="test")])
        llm = models.model_ollama
        print("✅ Using Ollama chat model")
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("💡 Tip: Make sure Ollama is installed and running. Visit: https://ollama.com/download")

# Exit if no language model is available
if not llm:
    print("❌ No language model available. Please configure either:")
    print("   1. OpenAI API (set OPENAI_API_KEY in .env file)")
    print("   2. Ollama (install and run: ollama serve)")
    exit(1)

# Initialize the vector store
vector_store = Chroma(
    collection_name="documents",
    embedding_function=embeddings,
    persist_directory="./DB/chroma_langchain_db"
)

# Define the chat prompt

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Answer the question based only on the data provided"),
        ("human", "Use the user question {input} to answer the question. Use only the {context} to answer the question.")
    ] 
)

#Define the retrieval chain

retriever = vector_store.as_retriever(search_kwargs={"k":10})

# Create the retrieval chain with the available LLM
combine_docs_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
retrieval_chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=combine_docs_chain)

print("✅ Chat system ready!")

# Main Loop

def main():
    import sys
    
    # Check if question is provided as command line argument
    if len(sys.argv) > 1:
        # Non-interactive mode for MCP server
        query = " ".join(sys.argv[1:])
        try:
            response = retrieval_chain.invoke({"input": query})
            print(response["answer"])
        except Exception as e:
            print(f"Error: {e}")
        return
    
    # Interactive mode
    print("\n=== MCP Server Chat Interface ===")
    print("Ask questions about the ingested documents. Type 'q', 'quit' or 'exit' to end.")
    print()
    
    while True:
        query = input("User: ")
        if query.lower() in ['q', 'quit', 'exit']:
            print("Goodbye!")
            break
        
        if not query.strip():
            continue
            
        try:
            print("🔍 Searching documents...")
            response = retrieval_chain.invoke({"input": query})
            print("Assistant:", response["answer"])
            print()
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try rephrasing your question.")
            print()

if __name__ == "__main__":
    main()
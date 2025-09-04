from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain 
from langchain_chroma import Chroma
from models import Models

# Initialize The Models (OpenAI only)
models = Models()

# Use OpenAI embeddings and chat model
embeddings = models.embeddings_openai
llm = models.model_openai
print("[SUCCESS] Using OpenAI embeddings and chat model")

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

print("[SUCCESS] Chat system ready!")

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
            print(f"[ERROR] Error: {e}")
            print("Please try rephrasing your question.")
            print()

if __name__ == "__main__":
    main()
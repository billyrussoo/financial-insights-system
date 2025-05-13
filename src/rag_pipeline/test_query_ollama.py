from query_ollama import run_llm

print("[🔎] Testing RAG-based query with FAISS + Ollama")

# Define a sample query and some fake document chunks
query = "What are some recent financial trends in the tech sector?"

documents = [
    "Apple's stock rose 5% in the last quarter amid strong iPhone sales.",
    "Google announced new AI models that could impact the advertising market.",
    "Meta is investing heavily in virtual reality, despite declining revenue in other sectors."
]

# Run the test query
response = run_llm(query, documents)

# Print the response
print("\n📄 LLM Response:\n")
print(response)

from embed_store import embed_documents, retrieve_top_k_chunks


docs = [
    "OpenAI has released a new version of ChatGPT based on the GPT-4 architecture.",
    "The stock market experienced a slight downturn following economic uncertainty.",
    "Bitcoin hit a new all-time high as investors pile into crypto."
]

# Step 1: Embed the documents
embed_documents(docs)

# Step 2: Query
results = retrieve_top_k_chunks("Tell me about the stock market")
print("\nTop matching chunks:")
for chunk in results:
    print("-", chunk)

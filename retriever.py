import os
from dotenv import load_dotenv
import openai
from qdrant_client import QdrantClient
from qdrant_client.http.models import SearchParams

# Load .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Setup Qdrant client
qdrant = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "policy_chunks"

def get_openai_embedding(text: str):
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def retrieve_relevant_chunks(query: str, top_k: int = 5):
    query_vector = get_openai_embedding(query)
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        search_params=SearchParams(hnsw_ef=128)
    )
    return [hit.payload.get("text", "") for hit in results]

# 🔁 Test the retriever
if __name__ == "__main__":
    query = "Generate offer letter for Martha Bennett"
    print(f"\n🔍 Query: {query}\n")
    chunks = retrieve_relevant_chunks(query)
    
    print("🧠 Retrieved Chunks:")
    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk #{i}:\n{chunk[:500]}")  # Truncate for readability

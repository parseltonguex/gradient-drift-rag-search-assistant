import json
import os
from tqdm import tqdm
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load Pinecone API key from .env
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Pinecone config
INDEX_NAME = "bmw-rag"
REGION = "us-east-1"
EMBEDDING_FILE = "data/processed/bmw_embeddings.jsonl"

# Initialise Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index("bmw-rag")

def load_embeddings(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def batch_upload(chunks, batch_size=100):
    batch = []
    for chunk in tqdm(chunks, desc="Uploading to Pinecone"):
        # Build Pinecone-compatible format
        vector = (
            chunk["id"],
            chunk["embedding"],
            {
                "text": chunk["text"],
                **chunk.get("metadata", {})
            }
        )
        batch.append(vector)

        if len(batch) == batch_size:
            index.upsert(vectors=batch)
            batch = []

    # Upload any remaining vectors
    if batch:
        index.upsert(vectors=batch)

if __name__ == "__main__":
    embeddings = load_embeddings(EMBEDDING_FILE)
    batch_upload(embeddings)
    print("✅ Embeddings uploaded to Pinecone.")

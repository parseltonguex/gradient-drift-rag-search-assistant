import os
import json
from dotenv import load_dotenv
from pinecone import Pinecone

# -----------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------------------------------------
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "bmw-rag")

# -----------------------------------------------------------
# INITIALIZE PINECONE CLIENT
# -----------------------------------------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# -----------------------------------------------------------
# FUNCTION: Retrieve Top-k Matches
# -----------------------------------------------------------
def retrieve_top_k(query_embedding: list, top_k: int = 5):
    """
    Query Pinecone for the top-k most similar vectors to the given embedding.

    Returns:
        A list of dictionaries with 'id', 'score', and 'text' fields.
    """
    try:
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        # Convert Pinecone response into clean Python dicts
        matches = []
        for match in results["matches"]:
            metadata = match.get("metadata", {})
            matches.append({
                "id": match["id"],
                "score": round(match["score"], 4),
                "text": metadata.get("text", ""),
            })

        return matches

    except Exception as e:
        print(f"[ERROR] Retrieval failed: {e}")
        raise

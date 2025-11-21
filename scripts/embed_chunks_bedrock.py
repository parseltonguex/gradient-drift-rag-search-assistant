import boto3
import json
import os
from tqdm import tqdm  # progress bar (install with `pip install tqdm`)

# Config
INPUT_CHUNKS = "data/processed/bmw_chunks.jsonl"
OUTPUT_EMBEDDINGS = "data/processed/bmw_embeddings.jsonl"
REGION = "us-east-1"  # update if Bedrock is in another region

# Create Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name=REGION)

def embed_text(text):
    """
    Send a text chunk to the Titan Embeddings model via Bedrock
    and return its vector representation.
    """
    body = {
        "inputText": text
    }

    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response["body"].read())
    return response_body["embedding"]

def main():
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_EMBEDDINGS), exist_ok=True)

    with open(INPUT_CHUNKS, "r", encoding="utf-8") as infile, \
         open(OUTPUT_EMBEDDINGS, "w", encoding="utf-8") as outfile:

        print(f"🔄 Generating embeddings for chunks in {INPUT_CHUNKS}...")

        for line in tqdm(infile, desc="Embedding chunks"):
            chunk = json.loads(line)
            text = chunk["text"]

            # Generate embedding
            embedding = embed_text(text)

            # Combine with metadata
            record = {
                "id": chunk["id"],
                "embedding": embedding,
                "text": text,
                "metadata": chunk["metadata"]
            }

            outfile.write(json.dumps(record) + "\n")

    print(f"✅ All embeddings generated and saved to {OUTPUT_EMBEDDINGS}")

if __name__ == "__main__":
    main()

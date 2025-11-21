import os
import json                     # <-- make sure this is imported here, at the top
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# -----------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------------------------------------
load_dotenv()

BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")

# -----------------------------------------------------------
# CREATE BEDROCK CLIENT
# -----------------------------------------------------------
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=BEDROCK_REGION
)

# -----------------------------------------------------------
# FUNCTION: Get Titan Embedding Vector
# -----------------------------------------------------------
def get_query_embedding(query_text: str):
    """
    Generate an embedding vector for a query using the
    Amazon Titan Embeddings model (via Bedrock Runtime).
    Returns a list of floats.
    """
    try:
        response = bedrock.invoke_model(
            modelId="amazon.titan-embed-text-v1",
            body=json.dumps({"inputText": query_text}),  # uses the imported json
            accept="application/json",
            contentType="application/json"
        )

        payload = response["body"].read().decode("utf-8")
        result = json.loads(payload)
        embedding = result.get("embedding", [])

        return embedding

    except ClientError as e:
        print(f"[ERROR] AWS Client error while generating embedding: {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error in get_query_embedding(): {e}")
        raise

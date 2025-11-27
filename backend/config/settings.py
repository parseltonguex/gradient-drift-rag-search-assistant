import os
from dotenv import load_dotenv

# -----------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------------------------------------
load_dotenv()

# AWS & Bedrock
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BEDROCK_REGION = os.getenv("BEDROCK_REGION") or os.getenv("AWS_REGION", "us-east-1")

# Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "bmw-rag")

# -----------------------------------------------------------
# MODEL MAP (Front-end dropdown → Bedrock modelId)
# -----------------------------------------------------------

MODEL_MAP = {
    "claude-sonnet": "arn:aws:bedrock:us-east-1:593793057732:inference-profile/us.anthropic.claude-3-sonnet-20240229-v1:0",
    "claude-haiku":  "arn:aws:bedrock:us-east-1:593793057732:inference-profile/us.anthropic.claude-3-haiku-20240307-v1:0",
    "titan-text":    "amazon.titan-text-lite-v1",
    "mistral":       "mistral.mistral-7b-instruct-v0:2"
}


# -----------------------------------------------------------
# APPLICATION CONSTANTS
# -----------------------------------------------------------
LOG_FILE = "backend/logs/requests.jsonl"
PROMPT_TEMPLATE_PATH = "backend/prompts/rag_template.txt"

# Safety defaults
DEFAULT_TOP_K = 5
MAX_TOKENS = 512
TEMPERATURE = 0.3

# -----------------------------------------------------------
# SUMMARY PRINT (optional debug)
# -----------------------------------------------------------
if __name__ == "__main__":
    print("✅ Settings loaded:")
    print(f" - Bedrock region: {BEDROCK_REGION}")
    print(f" - Pinecone index: {PINECONE_INDEX_NAME}")
    print(f" - Models: {list(MODEL_MAP.keys())}")

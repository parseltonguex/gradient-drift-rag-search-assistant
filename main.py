import traceback

try:
    # Local imports
  #  from auth_verify import verify_access_token // temporary disabled

    # FastAPI + Middleware
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse

    # Pydantic / Data models
    from pydantic import BaseModel

    # AWS + Utilities
    import boto3
    from mangum import Mangum
    import json
    import time
    import logging
    import os
    from datetime import datetime

except Exception as e:
    print("IMPORT ERROR:", e)
    traceback.print_exc()
    raise

# Local imports
from backend.services.embeddings import get_query_embedding
from backend.services.vector_store import retrieve_top_k
from backend.services.generate import generate_answer
from backend.config.settings import MODEL_MAP
from backend.security import enforce_rate_limit
from backend.auth_verify import verify_access_token



# -----------------------------------------------------------
# LOGGING SETUP (Force CloudWatch output)
# -----------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

# Remove any existing handlers Lambda might have added
for h in logger.handlers[:]:
    logger.removeHandler(h)

# Add our own handler that always writes to stdout
handler_stream = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
handler_stream.setFormatter(formatter)
logger.addHandler(handler_stream)

logger.info("Lambda logger initialised successfully.")
print("PRINT: Lambda module imported successfully.")

# -----------------------------------------------------------
# FASTAPI INITIALIZATION
# -----------------------------------------------------------
app = FastAPI(title="RAG Search Assistant")

# -----------------------------------------------------------
# CORS MIDDLEWARE (allow both S3 + CloudFront origins)
# -----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://rag-search-frontend.s3-website.eu-west-2.amazonaws.com",
        "https://d1pfw1640errhz.cloudfront.net",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------
# REQUEST MODEL
# -----------------------------------------------------------
class AskRequest(BaseModel):
    query: str
    model: str = "claude-sonnet"
    k: int = 5

# -----------------------------------------------------------
# ROUTES
# -----------------------------------------------------------
@app.get("/")
async def root():
    return {"status": "ok", "message": "RAG Search Assistant API running"}

def verify_access_token(auth_header):
    # Simulate successful Cognito JWT validation
    return {
        "sub": "test-user",
        "email": "laurence@example.com",
        "scope": "rag.search.invoke"
    }

@app.post("/api/ask")
async def ask(request: Request, body: AskRequest):
    # -----------------------------------------------------------
    # AUTHENTICATION CHECK
    # -----------------------------------------------------------
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")

    try:
        claims = verify_access_token(auth_header)
    except Exception as e:
        logger.warning(f"Unauthorized access attempt: {e}")
        # use JSONResponse so headers and content-type are correct
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    # -----------------------------------------------------------
    # RATE LIMIT
    # -----------------------------------------------------------
    deny = await enforce_rate_limit(request)
    if deny:
        return deny

    # -----------------------------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------------------------
    if not isinstance(body.query, str) or len(body.query) > 1000:
        return JSONResponse(status_code=400, content={"error": "Prompt too long or invalid"})

    start_time = time.time()
    cw = boto3.client("cloudwatch")

    try:
        logger.info(f"Received query: {body.query}")
        model_id = MODEL_MAP.get(body.model, MODEL_MAP["mistral"])
        logger.info(f"Model selected: {model_id}")
        logger.info("Starting embedding and retrieval...")

        query_embedding = get_query_embedding(body.query)
        matches = retrieve_top_k(query_embedding, top_k=body.k)
        context = "\n".join([m["text"] for m in matches])
        answer = generate_answer(model_id=model_id, question=body.query, context=context)

        latency_ms = round((time.time() - start_time) * 1000, 2)

        # Push custom metric to CloudWatch
        cw.put_metric_data(
            Namespace="RAGSearch",
            MetricData=[{
                "MetricName": "Latency_ms",
                "Unit": "Milliseconds",
                "Value": latency_ms
            }]
        )

        log_request(body.model, body.query, body.k, matches, answer, latency_ms)

        return {
            "model": body.model,
            "answer": answer,
            "matches": matches,
            "latency_ms": latency_ms
        }

    except Exception as e:
        logger.exception("Unhandled exception in /api/ask")
        return JSONResponse(status_code=500, content={"error": str(e)})



# -----------------------------------------------------------
# LOGGING FUNCTION
# -----------------------------------------------------------
def log_request(model: str, query: str, k: int, matches: list, answer: str, latency_ms: float):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "model": model,
        "query": query,
        "k": k,
        "match_ids": [m["id"] for m in matches],
        "scores": [m["score"] for m in matches],
        "context_length": sum(len(m["text"]) for m in matches),
        "answer_length": len(answer),
        "latency_ms": latency_ms,
    }
    logger.info(json.dumps(log_entry))


# -----------------------------------------------------------
# LAMBDA HANDLER
# -----------------------------------------------------------
handler = Mangum(app)

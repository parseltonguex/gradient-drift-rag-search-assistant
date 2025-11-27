import os
import json
import boto3
from dotenv import load_dotenv
from backend.config.settings import BEDROCK_REGION




# -----------------------------------------------------------
# INITIALIZE BEDROCK CLIENT
# -----------------------------------------------------------
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name=BEDROCK_REGION
)

# -----------------------------------------------------------
# FUNCTION: Generate Grounded Answer
# -----------------------------------------------------------
def generate_answer(model_id: str, question: str, context: str) -> str:
    """
    Uses an LLM on AWS Bedrock (Claude, Titan Text, Mistral, DeepSeek)
    to generate a grounded answer based on retrieved context.
    """

    # Load RAG prompt template
    template_path = os.path.join("backend", "prompts", "rag_template.txt")
    with open(template_path, "r") as f:
        prompt_template = f.read()

    # Inject context and question into the template
    prompt = (
        prompt_template
        .replace("{{CONTEXT}}", context)
        .replace("{{QUESTION}}", question)
    )

    # Prepare model-specific payload
    body = build_request_body(model_id, prompt)

    try:
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            accept="application/json",
            contentType="application/json"
        )

        # 🧩 helper function (inside generate_answer)
        def _read_body(resp):
            body_obj = resp.get("body")
            raw = body_obj.read() if hasattr(body_obj, "read") else body_obj
            if isinstance(raw, (bytes, bytearray)):
                raw = raw.decode("utf-8", errors="replace")
            return json.loads(raw)

        # ✅ use the helper
        response_body = _read_body(response)

        # TEMP (optional): print JSON once for debugging
        # print(json.dumps(response_body, indent=2)[:2000])

        # ---- Handle Anthropic Claude 3 messages API ----
        if (
            isinstance(response_body, dict)
            and response_body.get("role") == "assistant"
            and "content" in response_body
        ):
            for item in response_body["content"]:
                if item.get("type") == "text":
                    return item.get("text", "").strip()

        # ---- Handle alternate Claude formats ----
        if "output" in response_body:
            out = response_body["output"]
            if isinstance(out, list) and out:
                msg = out[0].get("message", {})
                for item in msg.get("content", []):
                    if item.get("type") == "text":
                        return item.get("text", "").strip()
            elif isinstance(out, dict):
                msg = out.get("message", {})
                for item in msg.get("content", []):
                    if item.get("type") == "text":
                        return item.get("text", "").strip()

        # ---- Other model families ----
        if "completion" in response_body:
            return response_body["completion"].strip()

        if "outputText" in response_body:
            return response_body["outputText"].strip()

        if "outputs" in response_body:
            out = response_body["outputs"]
            if isinstance(out, list) and out:
                return out[0].get("text", "").strip()

        # Fallback (shows JSON if nothing parsed)
        return json.dumps(response_body)[:500]

    except Exception as e:
        print(f"[ERROR] Bedrock generation failed: {e}")
        raise


# -----------------------------------------------------------
# FUNCTION: Build Request Body for Model Families
# -----------------------------------------------------------
def build_request_body(model_id: str, prompt: str) -> dict:
    """
    Builds and returns a valid request body for each supported model type.
    """

    # Anthropic Claude (Claude 3 family → Messages API)
    if "anthropic.claude" in model_id:
        return {
            "anthropic_version": "bedrock-2023-05-31",  # REQUIRED
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ],
            "max_tokens": 512,
            "temperature": 0.3
        }

    # Amazon Titan Text
    elif "amazon.titan-text" in model_id:
        return {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0.3,
                "topP": 0.9
            }
        }

    # DeepSeek
    elif "deepseek" in model_id:
        return {
            "input": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.3
            }
        }

    # Mistral
    elif model_id.startswith("mistral."):
        return {
            "prompt": prompt,
            "max_tokens": 512,
            "temperature": 0.3,
            "top_p": 0.9,
            "stop": []
        }

    else:
        raise ValueError(f"Unsupported model ID: {model_id}")

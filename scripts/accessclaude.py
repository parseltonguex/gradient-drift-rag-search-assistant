import boto3, json

client = boto3.client("bedrock", region_name="us-east-1")

response = client.put_use_case_for_model_access(
    modelIdentifier="anthropic.claude-3-sonnet-20240229-v1:0",
    useCaseDescription="RAG assistant for personal AWS learning and testing"
)

print(json.dumps(response, indent=2))

import pytest
from backend.services.generate import build_request_body, generate_answer


def test_build_request_body_structure():
    """Check model-specific request payloads are correct."""
    prompt = "Sample prompt"

    claude = build_request_body("anthropic.claude-3-sonnet-20240229", prompt)
    titan = build_request_body("amazon.titan-text-express-v1", prompt)
    deepseek = build_request_body("deepseek-v2", prompt)

    assert "prompt" in claude
    assert "inputText" in titan
    assert "input" in deepseek


@pytest.mark.skip(reason="Integration test requires Bedrock credentials")
def test_generate_answer_live_call():
    """Optional integration test — calls Bedrock directly if configured."""
    answer = generate_answer(
        model_id="anthropic.claude-3-sonnet-20240229",
        question="What is BMW?",
        context="BMW is a car manufacturer."
    )
    assert isinstance(answer, str)
    assert len(answer) > 0

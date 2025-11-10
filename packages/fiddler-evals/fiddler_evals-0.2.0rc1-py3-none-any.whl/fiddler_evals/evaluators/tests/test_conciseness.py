import json

import pytest
import responses

from fiddler_evals.constants import CONTENT_TYPE_HEADER_KEY, JSON_CONTENT_TYPE
from fiddler_evals.evaluators.conciseness import Conciseness
from fiddler_evals.pydantic_models.score import Score, ScoreStatus
from fiddler_evals.tests.constants import LLM_GATEWAY_CREDENTIAL, LLM_GATEWAY_MODEL, URL


@pytest.fixture()
def evaluator() -> Conciseness:
    """Create a Conciseness evaluator."""
    return Conciseness(model=LLM_GATEWAY_MODEL, credential=LLM_GATEWAY_CREDENTIAL)


@responses.activate
def test_conciseness_concise_response(evaluator: Conciseness) -> None:
    """When evaluating a concise response
    Then it should return score 1.0
    And should include proper reasoning."""

    # Mock the API response
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "is_concise",
                    "value": 1.0,
                    "label": "True",
                    "reasoning": "The response is direct and to the point without unnecessary details.",
                }
            ]
        },
        "api_version": "3.0",
        "kind": "NORMAL",
    }

    responses.post(
        url=f"{URL}/v3/evals/score",
        json=mock_response,
        headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
    )

    score = evaluator.score("The capital of France is Paris.")

    assert isinstance(score, Score)
    assert score.name == "is_concise"
    assert score.evaluator_name == "conciseness"
    assert score.value == 1.0
    assert score.label == "True"
    assert score.status == ScoreStatus.SUCCESS
    assert (
        score.reasoning
        == "The response is direct and to the point without unnecessary details."
    )

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "conciseness"
    assert request_body["parameters"] == {
        "credential": LLM_GATEWAY_CREDENTIAL,
        "model": LLM_GATEWAY_MODEL,
    }
    assert request_body["inputs"]["response"] == "The capital of France is Paris."


@responses.activate
def test_conciseness_verbose_response(evaluator: Conciseness) -> None:
    """When evaluating a verbose response
    Then it should return score 0.0
    And should include proper reasoning."""

    # Mock the API response
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "is_concise",
                    "value": 0.0,
                    "label": "False",
                    "reasoning": "The response contains unnecessary elaboration and verbose language.",
                }
            ]
        },
        "api_version": "3.0",
        "kind": "NORMAL",
    }

    responses.post(
        url=f"{URL}/v3/evals/score",
        json=mock_response,
        headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
    )

    verbose_answer = (
        "Well, that's a great question about France. Let me think about this..."
        "France is a beautiful country in Europe, and it has many wonderful cities..."
        "The capital city of France is Paris, which is located in the north-central part..."
    )

    score = evaluator.score(verbose_answer)

    assert isinstance(score, Score)
    assert score.name == "is_concise"
    assert score.evaluator_name == "conciseness"
    assert score.value == 0.0
    assert score.label == "False"
    assert score.status == ScoreStatus.SUCCESS
    assert (
        score.reasoning
        == "The response contains unnecessary elaboration and verbose language."
    )

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "conciseness"
    assert request_body["parameters"] == {
        "credential": LLM_GATEWAY_CREDENTIAL,
        "model": LLM_GATEWAY_MODEL,
    }
    assert request_body["inputs"]["response"] == verbose_answer


@responses.activate
def test_conciseness_missing_reasoning(evaluator: Conciseness) -> None:
    """When API response has no reasoning
    Then it should return score with None reasoning
    And should handle missing fields gracefully."""

    # Mock the API response without reasoning
    mock_response = {
        "data": {
            "scores": [
                {
                    "name": "is_concise",
                    "value": 1.0,
                    "label": "True",
                }
            ]
        },
        "api_version": "3.0",
        "kind": "NORMAL",
    }

    responses.post(
        url=f"{URL}/v3/evals/score",
        json=mock_response,
        headers={CONTENT_TYPE_HEADER_KEY: JSON_CONTENT_TYPE},
    )

    score = evaluator.score("The capital of France is Paris.")

    assert score.value == 1.0
    assert score.label == "True"
    assert score.reasoning is None

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "conciseness"
    assert request_body["parameters"] == {
        "credential": LLM_GATEWAY_CREDENTIAL,
        "model": LLM_GATEWAY_MODEL,
    }
    assert request_body["inputs"]["response"] == "The capital of France is Paris."


@responses.activate
def test_conciseness_api_error_handling(evaluator: Conciseness) -> None:
    """When API call raises an exception
    Then it should propagate the exception
    And should not return a score."""

    # Mock API error response
    responses.post(
        url=f"{URL}/v3/evals/score",
        json={"error": "Internal server error"},
        status=500,
    )

    with pytest.raises(Exception):
        evaluator.score("The capital of France is Paris.")

    # Verify the request was made correctly
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == f"{URL}/v3/evals/score"
    assert request.headers[CONTENT_TYPE_HEADER_KEY] == JSON_CONTENT_TYPE

    # Verify request body
    request_body = json.loads(request.body)
    assert request_body["evaluator_name"] == "conciseness"
    assert request_body["parameters"] == {
        "credential": LLM_GATEWAY_CREDENTIAL,
        "model": LLM_GATEWAY_MODEL,
    }
    assert request_body["inputs"]["response"] == "The capital of France is Paris."


@pytest.mark.parametrize(
    "response",
    [
        "",
        None,
        "   \t\n  ",
    ],
)
def test_conciseness_validation_errors(evaluator: Conciseness, response: str) -> None:
    """When providing invalid response
    Then it should raise appropriate ValueError
    And should not make API call."""

    with pytest.raises(
        ValueError, match="response is required for conciseness evaluation"
    ):
        evaluator.score(response)

    # Verify no API call was made
    assert len(responses.calls) == 0


@pytest.mark.parametrize(
    "model",
    [
        "",
        None,
    ],
)
def test_conciseness_with_invalid_model(model: str | None) -> None:
    """When providing invalid model
    Then it should raise appropriate ValueError
    And should not initialize the evaluator."""

    with pytest.raises(
        ValueError, match="model is required for LLMAAJ based evaluators"
    ):
        Conciseness(model=model, credential=LLM_GATEWAY_CREDENTIAL)


@pytest.mark.parametrize(
    "credential",
    [
        "",
        None,
    ],
)
def test_conciseness_with_empty_credential(credential: str | None) -> None:
    """When providing empty credential, it should initialize the evaluator."""

    evaluator = Conciseness(model=LLM_GATEWAY_MODEL, credential=credential)
    assert evaluator.model == LLM_GATEWAY_MODEL
    assert evaluator.credential == credential

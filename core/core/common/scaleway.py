import asyncio
import os
import httpx
from time import time
from typing import Any
from pydantic import BaseModel
from core.utils.logger import get_logger

logger = get_logger(__name__)

url = "https://api.scaleway.com/inference/v1/regions/fr-par"
headers = {
    "Content-Type": "application/json",
    "X-Auth-Token": os.getenv("SCW_SECRET_KEY", ""),
}


def list_models():
    response = httpx.get(f"{url}/models", headers=headers)
    response.raise_for_status()
    return response.json()


def deploy_model(model_id: str, model_name: str):
    payload = {
        "project_id": os.getenv("SCW_PROJECT_ID", ""),
        "model_id": model_id,
        "name": model_name,
        "node_type_name": "L4",
        "endpoints": [{"public_network": {}}],
    }
    response = httpx.post(f"{url}/deployments", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def list_deployments() -> dict:
    response = httpx.get(f"{url}/deployments", headers=headers)
    response.raise_for_status()
    return response.json()


def find_deployment(model_name: str) -> dict:
    deployments = list_deployments().get("deployments", [])
    for deployment in deployments:
        if deployment.get("name") == model_name:
            return deployment
    raise ValueError(f"No deployment found for model name: {model_name} \
        \nAvailable deployments: {[d.get('name') for d in deployments]}")


def get_deployment(deployment_id: str) -> dict:
    response = httpx.get(f"{url}/deployments/{deployment_id}", headers=headers)
    response.raise_for_status()
    return response.json()


def delete_deployment(deployment_id: str):
    response = httpx.delete(f"{url}/deployments/{deployment_id}", headers=headers)
    response.raise_for_status()
    return response.status_code == 204


class ChatCompletionParams(BaseModel):
    """All optional parameters for /v1/chat/completions.
    Only non-None fields are sent to the API.
    """

    # Sampling / generation control
    temperature: float | None = None  # 0.0 - 2.0
    top_p: float | None = None  # nucleus sampling, 0.0 - 1.0
    n: int | None = None  # number of completions to generate
    max_tokens: int | None = None  # deprecated in favor of max_completion_tokens
    max_completion_tokens: int | None = None
    stop: str | list[str] | None = None
    presence_penalty: float | None = None  # -2.0 - 2.0
    frequency_penalty: float | None = None  # -2.0 - 2.0
    logit_bias: dict[str, float] | None = None
    seed: int | None = None

    # Output shaping
    response_format: dict[str, Any] | None = None  # e.g. {"type": "json_object"}
    logprobs: bool | None = None
    top_logprobs: int | None = None  # requires logprobs=True, 0-20

    # Tool / function calling
    tools: list[dict[str, Any]] | None = None
    tool_choice: str | dict[str, Any] | None = None
    parallel_tool_calls: bool | None = None

    # Streaming
    stream: bool | None = None
    stream_options: dict[str, Any] | None = None

    # Misc
    user: str | None = None  # end-user identifier for abuse monitoring
    service_tier: str | None = None
    store: bool | None = None
    metadata: dict[str, str] | None = None
    modalities: list[str] | None = None


def get_completion(messages: list, model_name: str, deployment_url: str, params: ChatCompletionParams):
    url = deployment_url + "/v1/chat/completions"
    payload = {
        "model": model_name,
        "messages": messages,
        **params.model_dump(exclude_unset=True),
    }
    start_time = time()
    response = httpx.post(url, headers=headers, json=payload)
    response.raise_for_status()
    content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    logger.debug(f"Completion took {(time()-start_time)}s")
    return content


async def get_batch_completions(
    batch: list[list],  # list of messages lists
    model_name: str,
    deployment_url: str,
    params: ChatCompletionParams,
) -> list[str]:
    async def get_completion_async(client: httpx.AsyncClient, messages: list) -> str:
        url = deployment_url + "/v1/chat/completions"
        payload = {
            "model": model_name,
            "messages": messages,
            **params.model_dump(exclude_unset=True),
        }
        # start_time = time()
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        # logger.debug(f"Completion took {(time() - start_time)}s")
        return content

    async with httpx.AsyncClient(timeout=60) as client:
        start_time = time()
        tasks = [get_completion_async(client, messages) for messages in batch]
        contents = await asyncio.gather(*tasks)
        logger.debug(f"Batch completion took {(time() - start_time)}s")
        return contents

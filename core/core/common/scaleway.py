import os
import httpx

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


def list_deployments():
    response = httpx.get(f"{url}/deployments", headers=headers)
    response.raise_for_status()
    return response.json()


def get_deployment(deployment_id: str):
    response = httpx.get(f"{url}/deployments/{deployment_id}", headers=headers)
    response.raise_for_status()
    return response.json()


def delete_deployment(deployment_id: str):
    response = httpx.delete(f"{url}/deployments/{deployment_id}", headers=headers)
    response.raise_for_status()
    return response.status_code == 204

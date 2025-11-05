from huggingface_hub import list_models, model_info

OWNER = "dataesr"


def list(owner: str = OWNER, limit: int = 100):
    models = list_models(author=owner, limit=limit, fetch_config=True)
    models = [model.__dict__ for model in models]
    return models


def get(owner: str, name: str):
    model = model_info(repo_id=f"{owner}/{name}")
    return model.__dict__

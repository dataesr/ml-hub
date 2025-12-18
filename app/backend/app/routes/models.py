from fastapi import APIRouter
from huggingface_hub import list_models, model_info

router = APIRouter(tags=["models"])


@router.get("/models")
@router.get("/models/{owner}")
def models_list(owner: str = "dataesr", limit: int = 100):
    models = list_models(author=owner, limit=limit, fetch_config=True)
    models = [model.__dict__ for model in models]
    return models


@router.get("/models/{owner}/{name}")
def models_get(owner: str, name: str):
    model = model_info(repo_id=f"{owner}/{name}")
    return model.__dict__

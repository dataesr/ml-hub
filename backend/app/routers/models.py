from fastapi import APIRouter, HTTPException
from huggingface_hub import list_models, model_info

router = APIRouter()


@router.get("/models")
def hf_list_models(owner: str = None, limit: int = 100):
    try:
        models = list_models(author=owner, limit=limit, fetch_config=True)
        models = [model.__dict__ for model in models]
        return models
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/models/{owner}/{name}")
def hf_get_model(owner: str, name: str):
    try:
        model = model_info(repo_id=f"{owner}/{name}")
        return model.__dict__
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))

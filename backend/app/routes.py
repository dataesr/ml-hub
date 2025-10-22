from fastapi import APIRouter
from app.hf import hf_list_models, hf_model_info

router = APIRouter()


### huggingface hub
@router.get("/model/{owner}/{name}")
async def hf_get_model(owner: str, name: str):
    model = hf_model_info(f"{owner}/{name}")
    return model


@router.get("/models/{owner}")
async def hf_get_models(owner: str):
    models = hf_list_models(owner)
    return models

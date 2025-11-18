from fastapi import APIRouter, HTTPException
import app.models.service as models_svc

router = APIRouter()


@router.get("/models")
@router.get("/models/{owner}")
def models_list(owner: str = models_svc.OWNER, limit: int = 100):
    models = models_svc.get_all(owner, limit)
    return models


@router.get("/models/{owner}/{name}")
def models_get(owner: str, name: str):
    model = models_svc.get(owner, name)
    return model

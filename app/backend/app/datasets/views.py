from fastapi import APIRouter
from app.datasets import service as datasets_svc

router = APIRouter(tags=["datasets"])


@router.get("/datasets")
@router.get("/datasets/{owner}")
def datasets_list(owner: str = datasets_svc.OWNER, limit: int = 100):
    datasets = datasets_svc.get_all(owner, limit)
    return datasets


@router.get("/datasets/{owner}/{name}")
def datasets_get(owner: str, name: str):
    dataset = datasets_svc.get(owner, name)
    return dataset

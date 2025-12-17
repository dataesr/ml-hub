from fastapi import APIRouter
from huggingface_hub import dataset_info, list_datasets

router = APIRouter(tags=["datasets"])


@router.get("/datasets")
@router.get("/datasets/{owner}")
def datasets_list(owner: str = "dataesr", limit: int = 100):
    datasets = list_datasets(author=owner, limit=limit)
    datasets = [dataset.__dict__ for dataset in datasets]
    return datasets


@router.get("/datasets/{owner}/{name}")
def datasets_get(owner: str, name: str):
    dataset = dataset_info(repo_id=f"{owner}/{name}")
    return dataset.__dict__

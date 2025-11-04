from fastapi import APIRouter, HTTPException
from huggingface_hub import dataset_info, list_datasets

router = APIRouter()


@router.get("/datasets")
def hf_list_datasets(owner: str = None, limit: int = 100):
    try:
        datasets = list_datasets(author=owner, limit=limit)
        datasets = [dataset.__dict__ for dataset in datasets]
        return datasets
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/datasets/{owner}/{name}")
async def hf_get_dataset(owner: str, name: str):
    try:
        dataset = dataset_info(repo_id=f"{owner}/{name}")
        return dataset.__dict__
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))

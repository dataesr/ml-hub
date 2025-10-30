from fastapi import APIRouter, HTTPException
from huggingface_hub import list_models, model_info, dataset_info, list_datasets
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/hf")


@router.get("/dataset/{owner}/{name}")
async def hf_get_dataset(owner: str, name: str):
    try:
        dataset = dataset_info(repo_id=f"{owner}/{name}")
        return dataset.__dict__
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/datasets/{owner}")
def hf_list_datasets(owner: str = None, limit: int = 100):
    datasets = list_datasets(author=owner, limit=limit)
    datasets = [dataset.__dict__ for dataset in datasets]
    # logger.debug(f"{models =}")
    return datasets


@router.get("/model/{owner}/{name}")
async def hf_get_model(owner: str, name: str):
    try:
        model = model_info(repo_id=f"{owner}/{name}")
        return model.__dict__
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/models/{owner}")
def hf_list_models(owner: str = None, limit: int = 100):
    models = list_models(author=owner, limit=limit, fetch_config=True)
    models = [model.__dict__ for model in models]
    # logger.debug(f"{models =}")
    return models

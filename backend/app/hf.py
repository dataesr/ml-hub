from fastapi import HTTPException
from huggingface_hub import list_models, model_info, dataset_info, list_datasets
from huggingface_hub.errors import RepositoryNotFoundError
from app.logger import get_logger

logger = get_logger(__name__)


def hf_dataset_info(dataset_id: str):
    dataset = dataset_info(repo_id=dataset_id)
    return dataset.__dict__


def hf_list_datasets(owner: str = None, limit: int = 100):
    datasets = list_datasets(author=owner, limit=limit)
    datasets = [dataset.__dict__ for dataset in datasets]
    # logger.debug(f"{models =}")
    return datasets


def hf_model_info(model_id: str):
    model = model_info(repo_id=model_id)
    return model.__dict__


def hf_list_models(owner: str = None, limit: int = 100):
    models = list_models(author=owner, limit=limit, fetch_config=True)
    models = [model.__dict__ for model in models]
    # logger.debug(f"{models =}")
    return models

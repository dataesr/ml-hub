import os
from huggingface_hub import dataset_info, list_datasets
from app.logger import get_logger

logger = get_logger(__name__)


def get_all(owner: str, limit: int = 100):
    datasets = list_datasets(author=owner, limit=limit)
    datasets = [dataset.__dict__ for dataset in datasets]
    return datasets


def get(owner: str, name: str):
    dataset = dataset_info(repo_id=f"{owner}/{name}")
    return dataset.__dict__

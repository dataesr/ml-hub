import os
from huggingface_hub import dataset_info, list_datasets
from ai_core.cloud.storage import ovhai_object_download, ovhai_object_list, ovhai_object_upload
from app.datasets.schemas import DatasetConfig
from app.logger import get_logger
from app.utils import json_read, json_write, timestamp

logger = get_logger(__name__)

CONTAINER_DATASETS = "llm-datasets"
FOLDER_EXTRAS = "extras/"
FOLDER_TMP = "tmp/"
OWNER = "dataesr"

def get_all(owner: str, limit: int = 100):
    datasets = list_datasets(author=owner, limit=limit)
    datasets = [dataset.__dict__ for dataset in datasets]
    return datasets


def get(owner: str, name: str):
    dataset = dataset_info(repo_id=f"{owner}/{name}")
    return dataset.__dict__

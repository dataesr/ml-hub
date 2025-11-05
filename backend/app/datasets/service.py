from huggingface_hub import dataset_info, list_datasets
from app.ovhai import ovhai_object_list, ovhai_object_upload

CONTAINER_DATASETS = "llm-datasets"
FOLDER_CONFIGS = "configs/"
OWNER = "dataesr"


def list(owner: str = OWNER, limit: int = 100):
    datasets = list_datasets(author=owner, limit=limit)
    datasets = [dataset.__dict__ for dataset in datasets]
    return datasets


def get(owner: str, name: str):
    dataset = dataset_info(repo_id=f"{owner}/{name}")
    return dataset.__dict__


def list_configs():
    configs = ovhai_object_list(CONTAINER_DATASETS, FOLDER_CONFIGS)
    return configs


def get_config():
    return None


def add_config():
    return None

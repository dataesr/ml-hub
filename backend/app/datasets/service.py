import os
import uuid
from huggingface_hub import dataset_info, list_datasets
from app.ovhai import ovhai_object_download, ovhai_object_list, ovhai_object_upload
from app.datasets.schemas import DatasetConfig
from app.logger import get_logger
from app.utils import json_read, json_write

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


def list_configs():
    configs = ovhai_object_list(CONTAINER_DATASETS, FOLDER_EXTRAS)
    return configs


def create_config(extras: dict):
    config_name = extras.get("name")
    if not config_name:
        config_name = f"{extras.get('dataset_name')}/{str(uuid.uuid4())}"
    config = DatasetConfig(name=config_name, **extras)
    return config


def get_config(name: str):
    configs = ovhai_object_list(CONTAINER_DATASETS, FOLDER_EXTRAS)
    remote_path = os.path.join(FOLDER_EXTRAS, name)
    if not remote_path.endswith(".json"):
        remote_path += ".json"
    keys = [str(config.get("key", "")) for config in configs]
    if remote_path not in keys:
        raise FileNotFoundError(f"Config {name} (path={remote_path}) not found on storage")
    disk_path = ovhai_object_download(remote_path, CONTAINER_DATASETS, FOLDER_TMP, FOLDER_EXTRAS)
    if not os.path.isfile(disk_path):
        raise FileNotFoundError(f"Config {name} error while downloading")
    data = json_read(disk_path, remove=True)
    config = create_config(data)
    return config


def add_config(config: DatasetConfig):
    config_name = config.name
    config_content = config.model_dump(mode="json")
    # logger.debug(f"{config_content=}")
    path = json_write(path=os.path.join(FOLDER_TMP, config_name), data=config_content)
    ovhai_object_upload(path, CONTAINER_DATASETS, FOLDER_EXTRAS, FOLDER_TMP)
    os.remove(path)
    return config_name

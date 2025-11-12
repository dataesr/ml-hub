import os
import uuid
from huggingface_hub import dataset_info, list_datasets
from app.ovhai import ovhai_object_download, ovhai_object_list, ovhai_object_upload
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


def _configs_get_folder(dataset_name: str = None):
    folder = FOLDER_EXTRAS
    if dataset_name:
        folder = os.path.join(FOLDER_EXTRAS, dataset_name)
    if not folder.endswith("/"):
        folder += "/"
    return folder


def _config_get_storage_path(config_name: str, dataset_name: str = None):
    full_name = config_name
    if dataset_name:
        full_name = os.path.join(dataset_name, full_name)
    if not full_name.endswith(".json"):
        full_name += ".json"
    storage_path = os.path.join(FOLDER_EXTRAS, full_name)
    return storage_path


def list_configs(dataset_name: str = None):
    prefix = _configs_get_folder(dataset_name)
    objects = ovhai_object_list(CONTAINER_DATASETS, prefix)
    configs = []
    for obj in objects:
        key: str = obj.get("key", "")
        config_name = key.removeprefix(prefix).removesuffix(".json")
        configs.append(
            {
                "dataset_name": dataset_name,
                "config_name": config_name,
                "storage_path": key,
                "size": obj.get("size"),
                "last_modified": obj.get("last_modified"),
            }
        )
    return configs


def create_config(extras: dict):
    config_name = extras.pop("name")
    if not config_name:
        config_name = timestamp(print_time=False)
    config = DatasetConfig(name=config_name, **extras)
    logger.debug(f"{config_name}: {config=}")
    return config


def get_config(config_name: str, dataset_name: str = None):
    configs = list_configs(dataset_name)
    storage_path = _config_get_storage_path(config_name, dataset_name)
    found_paths = [config.get("storage_path") for config in configs]
    if storage_path not in found_paths:
        raise FileNotFoundError(f"Config {config_name} (path={storage_path}) not found on storage")
    file_path = ovhai_object_download(storage_path, CONTAINER_DATASETS)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Config {config_name} error while downloading")
    data = json_read(file_path, remove=True)
    config = create_config(data)
    return config


def add_config(config: DatasetConfig):
    storage_path = _config_get_storage_path(config.name, config.dataset_name)
    config_content = config.model_dump(mode="json")
    # logger.debug(f"{config_content=}")
    file_path = json_write(path=storage_path, data=config_content)
    ovhai_object_upload(file_path, CONTAINER_DATASETS)
    os.remove(file_path)
    return storage_path

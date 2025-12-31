import os
from datasets import Dataset, load_dataset
from ai_core.cloud.storage import ovhai_object_download
from ai_core.cloud.constants import DATASETS_CONTAINER
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


def load_from_storage(path: str, container: str) -> Dataset:
    file_path = ovhai_object_download(path, container)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Error while downloading {path}")
    dataset = load_dataset("json", data_files={"file": [file_path]}, split="file")
    os.remove(file_path)
    return dataset


def load_from_local(path: str) -> Dataset:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File {path} not found on disk")
    dataset = load_dataset("json", data_files={"file": [path]}, split="file")
    return dataset


def load_from_hf(dataset_name: str, split: str | None = None) -> Dataset:
    dataset = load_dataset(dataset_name, split=split)
    return dataset


def load(path_or_name: str, split: str | None = None) -> Dataset:
    try:
        logger.debug(f"Trying to load {path_or_name} from HuggingFace...")
        dataset = load_dataset(path_or_name, split=split)
    except Exception as error:
        logger.debug(f"Error while loading from HuggingFace: {error}")
        logger.debug("Trying to load from local disk...")
        local_path = os.path.join(DATASETS_CONTAINER, path_or_name)
        dataset = load_from_local(local_path)

    if dataset:
        logger.debug(f"✅ Dataset {path_or_name} loaded!")
        logger.debug(f"Dataset schema: {dataset.features}")
        logger.debug(f"Dataset size: {len(dataset)}")
        logger.debug(f"Dataset sample: {dataset[0]}")
    else:
        logger.error(f"Error while loading {path_or_name}")
        raise Exception(f"Error while loading {path_or_name}")

    return dataset

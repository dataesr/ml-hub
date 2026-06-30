import os
from datasets import Dataset, load_dataset
from core.cloud.storage import ovhai_object_download
from core.cloud.constants import DATASETS_CONTAINER, DATASETS_VOLUME
from core.utils.logger import get_logger

logger = get_logger(__name__)


def load_from_storage(path: str, container: str) -> Dataset:
    file_path = ovhai_object_download(path, container)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Error while downloading {path}")
    dataset: Dataset = load_dataset("json", data_files={"file": [file_path]}, split="file")
    os.remove(file_path)
    return dataset


def load_from_local(path: str) -> Dataset:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File {path} not found on disk")
    dataset: Dataset = load_dataset("json", data_files={"file": [path]}, split="file")
    return dataset


def load_from_hf(dataset_name: str, split: str | None = None) -> Dataset:
    dataset: Dataset = load_dataset(dataset_name, split=split)  # ty:ignore[invalid-assignment]
    return dataset


def load(path_or_name: str, split: str | None = None) -> Dataset:
    try:
        logger.debug(f"Trying to load {path_or_name} from HuggingFace...")
        dataset: Dataset = load_dataset(path_or_name, split=split)  # ty:ignore[invalid-assignment]
    except Exception as error:
        logger.debug(f"Error while loading from HuggingFace: {error}")
        try:
            logger.debug("Trying to load from local storage...")
            local_path = os.path.join(DATASETS_VOLUME, path_or_name)
            dataset = load_from_local(local_path)
        except Exception as error:
            logger.debug(f"Error while loading from local storage: {error}")
            try:
                logger.debug("Trying to load from cloud storage...")
                dataset = load_from_storage(path_or_name, container=DATASETS_CONTAINER)
            except Exception as error:
                logger.error(f"Error while loading from cloud storage: {error}")
                raise Exception(f"Failed to load dataset {path_or_name}")

    if dataset:
        logger.debug(f"✅ Dataset {path_or_name} loaded!")
        logger.debug(f"Dataset schema: {dataset.features}")
        logger.debug(f"Dataset size: {len(dataset)}")
        logger.debug(f"Dataset sample: {dataset[0]}")
    else:
        logger.error(f"Error while loading {path_or_name}")
        raise Exception(f"Error while loading {path_or_name}")

    return dataset

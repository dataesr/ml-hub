from datasets import Dataset
from core.datasets.constants import INPUT_COLUMN
from core.utils.logger import get_logger

logger = get_logger(__name__)


def get_commit_hash(dataset: Dataset) -> str | None:
    """
    Retrieve commit hash from dataset checksums

    Args:
        dataset (Dataset): dataset

    Returns:
        commit_hash (str): dataset commit hash
    """
    commit_hash = None

    if not isinstance(dataset, Dataset):
        return commit_hash

    checksums = dataset.info.download_checksums
    if isinstance(checksums, dict) and checksums:
        checksums_list = list(checksums.keys())
        checksum_file = checksums_list[0].split("@")[1]  # ty:ignore[unresolved-attribute]
        commit_hash = checksum_file.split("/")[0]
    return commit_hash


def get_prompts(data: Dataset) -> list[str]:
    input_col = INPUT_COLUMN
    if input_col not in data.column_names:
        raise ValueError(f"Column {input_col} not found on data! Set env var 'INPUT_COLUMN' to select the column name.")

    prompts = list(data[input_col])
    return prompts


def should_use_chat_format(config_format: str | None = None, dataset_chat_template=None):
    if config_format == "chat":
        logger.debug("Format set to 'chat'")
        return True
    elif config_format == "text":
        logger.debug("Format set to 'text'")
        return False
    else:
        if dataset_chat_template is not None:
            logger.debug("Format automatically set to 'chat'")
            return True
        else:
            logger.debug("Format automatically set to 'text'")
            return False

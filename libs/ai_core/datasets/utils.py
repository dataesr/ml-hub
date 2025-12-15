from datasets import Dataset
from ai_core.utils.logger import get_logger

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
        checksum_file = checksums_list[0].split("@")[1]
        commit_hash = checksum_file.split("/")[0]
    return commit_hash


def should_use_conversational_format(dataset_format_arg: str = None, dataset_chat_template=None):
    if dataset_format_arg == "conversational":
        logger.debug("Format set to 'conversational'")
        return True
    elif dataset_format_arg == "text":
        logger.debug("Format set to 'text'")
        return False
    else:
        if dataset_chat_template is not None:
            logger.debug("Format automatically set to 'conversational'")
            return True
        else:
            logger.debug("Format automatically set to 'text'")
            return False

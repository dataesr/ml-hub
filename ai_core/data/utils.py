from datasets import Dataset


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

import os
from ai_core.utils.logger import get_logger
from huggingface_hub import create_repo, upload_folder

logger = get_logger(__name__)


def push_folder_to_hf(folder_path: str, repo_id: str, private=False) -> str:
    """
    Uploads a model directory to the Hugging Face Hub.

    Args:
    - folder_path (str): Path to the saved model folder (should include config.json, pytorch_model.bin, tokenizer, etc.)
    - repo_id (str): The model repo ID on Hugging Face
    - private (bool): If True, creates a private repo

    Returns:
    - hf_hash (str): Hugging Face commit hash id
    """

    logger.info(f"Start uploading folder from {folder_path} to https://huggingface.co/{repo_id}")

    # Get hugging face token from env
    token = os.getenv("HF_TOKEN")
    if not token:
        logger.warning("'HF_TOKEN' not found in env, can't push to huggingface")
        return None

    if not os.path.exists(folder_path):
        logger.warning(f"Folder {folder_path} does not exist, can't push folder to huggingface")
        return None

    # Create the repo if it doesn't exist
    repo_url = create_repo(repo_id, private=private, token=token, exist_ok=True)
    logger.debug(f"repo_url = {repo_url}")

    # Upload all contents of the folder
    commit_info = upload_folder(
        folder_path=folder_path,
        path_in_repo=".",  # Upload directly into the repo root
        repo_id=repo_id,
        token=token,
    )
    logger.debug(f"commit_info = {commit_info.__dict__}")
    logger.info(f"✅ Folder uploaded to https://huggingface.co/{repo_id}")

    return commit_info.oid


def push_model_to_hf(model_dir: str, raise_error: bool = False) -> str:
    repo_id = os.getenv("HF_PUSH_REPO")

    if not repo_id:
        if raise_error:
            raise ValueError(f"Env var 'HF_PUSH_REPO' not defined, can't push model to huggingface")
        logger.warning("Env var 'HF_PUSH_REPO' not defined, can't push model to huggingface")
        return None

    logger.info(f"Pushing folder (from {model_dir}) to HF ({repo_id})...")

    # Upload model to hub
    hf_hash = push_folder_to_hf(model_dir, repo_id=repo_id, private=True)
    if hf_hash:
        logger.info(f"✅ Successfully pushed model to huggingface ({hf_hash=})")
    return hf_hash

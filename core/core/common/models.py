from typing import no_type_check
import os
from huggingface_hub import create_repo, upload_folder
from core.utils.logger import get_logger

logger = get_logger(__name__)


@no_type_check
def merge_adapters_to_model(
    name_or_path: str,
    merged_dir: str,
    base_model_name_or_path: str | None = None,
    tokenizer_name_or_path: str | None = None,
) -> str:
    """Merge a PEFT adapter into its base model and save the merged model directory."""
    # Heavy dependencies are imported lazily to avoid import-time requirements.
    import torch
    from peft import PeftConfig, PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    logger.info(f"Start merging adapters from {name_or_path}")

    peft_config = PeftConfig.from_pretrained(name_or_path)
    inferred_base_model = peft_config.base_model_name_or_path
    resolved_base_model = base_model_name_or_path or inferred_base_model

    if not resolved_base_model:
        raise ValueError(
            "Base model is required to merge adapters. "
            "Provide base_model_name_or_path or ensure adapters_config.json contains base_model_name_or_path."
        )

    if base_model_name_or_path and inferred_base_model and base_model_name_or_path != inferred_base_model:
        logger.warning(
            "Overriding base model from adapters config "
            f"({inferred_base_model}) with explicit value ({base_model_name_or_path})."
        )

    torch_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    device_map = "auto" if torch.cuda.is_available() else None

    logger.info(f"Loading base model: {resolved_base_model}")
    base_model = AutoModelForCausalLM.from_pretrained(
        resolved_base_model,
        device_map=device_map,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
    )

    logger.info("Loading adapters into base model")
    peft_model = PeftModel.from_pretrained(base_model, name_or_path)
    model_merged = peft_model.merge_and_unload()

    os.makedirs(merged_dir, exist_ok=True)
    model_merged.save_pretrained(merged_dir, safe_serialization=True)

    tokenizer_source = tokenizer_name_or_path or name_or_path
    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_source, use_fast=True)
    except Exception as error:
        logger.warning(f"Failed to load tokenizer from {tokenizer_source} ({error}). Falling back to base model tokenizer.")
        tokenizer = AutoTokenizer.from_pretrained(resolved_base_model, use_fast=True)
    tokenizer.save_pretrained(merged_dir)

    del peft_model
    del base_model
    del model_merged
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    logger.info(f"✅ Model merged and saved to {merged_dir}")
    return merged_dir


def push_folder_to_hf(folder_path: str, repo_id: str, private=False) -> str | None:
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


def push_model_to_hf(model_dir: str, repo_id: str | None = None, raise_error: bool = False) -> str | None:
    repo_id = repo_id or os.getenv("HF_PUSH_REPO")

    if not repo_id:
        if raise_error:
            raise ValueError("HF repo ID not defined, can't push model to huggingface")
        logger.warning("HF repo ID not defined, can't push model to huggingface")
        return None

    logger.info(f"Pushing folder (from {model_dir}) to HF ({repo_id})...")

    # Upload model to hub
    hf_hash = push_folder_to_hf(model_dir, repo_id=repo_id, private=True)
    if hf_hash:
        logger.info(f"✅ Successfully pushed model to huggingface ({hf_hash=})")
    return hf_hash

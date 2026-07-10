"""Merge LoRA/PEFT adapters into a base model."""

import os
from typing import Optional
from pydantic import Field, BaseModel
from core.common.models import merge_adapters_to_model, push_model_to_hf
from core.utils.files import folder_create
from core.utils.logger import get_logger

logger = get_logger(__name__)


class MergeAdaptersArgs(BaseModel):
    """Arguments for the merge adapters job."""

    name_or_path: str = Field(..., description="HF name or path of the adapters to merge")
    base_model_name_or_path: Optional[str] = Field(None, description="HF name or path of the base model")
    output_dir: Optional[str] = Field(None, description="Directory where the merged model will be saved")
    hf_push_repo: Optional[str] = Field(None, description="HuggingFace repo ID to push the model to.")


def run_merge_adapters(args: MergeAdaptersArgs):
    """Merge adapters to a base model and save merged model."""
    # Keep output paths deterministic and filesystem-safe for both local and HF names.
    safe_name = args.name_or_path.replace("\\", "_").replace("/", "_").replace(":", "_").strip("_")
    model_dir: str = folder_create(os.path.join("jobs", "merge-adapters", safe_name))
    merged_dir = folder_create(args.output_dir or os.path.join(model_dir, "merged"))

    logger.info(f"Merging adapters from {args.name_or_path}")
    if args.base_model_name_or_path:
        logger.info(f"Using explicit base model: {args.base_model_name_or_path}")
    else:
        logger.info("No explicit base model provided. Will use adapters config base_model_name_or_path.")

    merge_adapters_to_model(
        name_or_path=args.name_or_path,
        merged_dir=merged_dir,
        base_model_name_or_path=args.base_model_name_or_path,
    )

    push_model_to_hf(merged_dir, args.hf_push_repo)
    return merged_dir

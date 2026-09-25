"""Pretrain a model with TorchTitan."""
from core.utils.files import folder_create

import os
import subprocess
from typing import Optional
from pydantic import BaseModel, Field
from core.common.datasets import DatasetConfig, download_dataset
from core.common.mlflow import MLflowRun
from core.common.models import download_model, upload_model
from core.utils.cmd import run_cmd
from core.utils.logger import get_logger

logger = get_logger(__name__)


class TorchTitanArgs(BaseModel):
    """Arguments for a TorchTitan pretraining run."""

    model_name: str = Field(..., description="HuggingFace model repository to download")
    dataset: DatasetConfig = Field(..., description="Dataset to prepare for TorchTitan")
    module_name: str = Field(..., description="TorchTitan configuration module")
    config_name: str = Field(..., description="TorchTitan configuration function")
    hf_push_repo: Optional[str] = Field(None, description="HuggingFace repo ID to push the model to.")


def run_torchtitan(args: TorchTitanArgs, mlf: MLflowRun):
    """Download model assets and start TorchTitan's distributed trainer."""
    mlf.start_run(f"torchtitan-{args.model_name}", tags={"run_type": "pretraining"})

    ### --- Download model and dataset ---
    model_dir: str = folder_create(os.path.join("jobs", args.model_name))
    output_dir = os.path.join(model_dir, "output")
    assets_dir = os.path.join(model_dir, "assets")
    assets_dir = download_model(args.model_name, assets_dir)

    # TODO: Download tokenizer if different from model

    dataset_name = os.path.splitext(os.path.basename(args.dataset.path))[0]
    dataset_path = os.path.join(model_dir, "datasets", f"{dataset_name}-{args.dataset.split}.jsonl")
    dataset_path = download_dataset(args.dataset.path, dataset_path, split=args.dataset.split)

    ### --- Training ---
    env = os.environ.copy()
    env["MODULE"] = args.module_name
    env["CONFIG"] = args.config_name
    env.setdefault("NGPU", "1")

    command = [
        "/torchtitan/run_train.sh",
        "--dump_folder",
        output_dir,
        "--hf_assets_path",
        assets_dir,
        "--checkpointer.initial_load_path",
        assets_dir,
        "--dataloader.dataset.dataset.source.load_dataset_kwargs.data_files",
        dataset_path,
    ]

    logger.info(f"Starting TorchTitan: {' '.join(command)}")
    run_cmd(command, streaming=True, env=env)
    logger.info("✅ TorchTitan pretraining completed successfully.")

    ### --- Push model ---
    # upload_model(model_dir, args.hf_push_repo)

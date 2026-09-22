"""Pretrain a model with TorchTitan."""

import os
import subprocess
from pydantic import BaseModel, Field
from core.common.datasets import DatasetConfig, download_dataset
from core.common.mlflow import MLflowRun
from core.common.models import download_model
from core.utils.logger import get_logger

logger = get_logger(__name__)


class TorchTitanArgs(BaseModel):
    """Arguments for a TorchTitan pretraining run."""

    model_name: str = Field(..., description="HuggingFace model repository to download")
    dataset: DatasetConfig = Field(..., description="Dataset to prepare for TorchTitan")
    module: str = Field(..., description="TorchTitan configuration module")
    config: str = Field(..., description="TorchTitan configuration function")


def run_torchtitan(args: TorchTitanArgs, mlf: MLflowRun):
    """Download model assets and start TorchTitan's distributed trainer."""
    mlf.start_run(f"torchtitan-{args.model_name}", tags={"run_type": "pretraining"})

    model_dir = os.path.join("assets", "hf", args.model_name.split("/")[-1])
    download_model(args.model_name, model_dir)

    dataset_name = os.path.splitext(os.path.basename(args.dataset.path))[0]
    dataset_path = os.path.join("jobs", "datasets", f"{dataset_name}-{args.dataset.split}.jsonl")
    download_dataset(args.dataset.path, dataset_path, split=args.dataset.split)

    # environment = {}
    # environment["TORCHTITAN_DATASET_PATH"] = dataset_path

    nproc_per_node = os.getenv("NGPU", "8")
    command = [
        "torchrun",
        f"--nproc_per_node={nproc_per_node}",
        "-m",
        "torchtitan.train",
        "--module",
        args.module,
        "--config",
        args.config,
    ]
    logger.info(f"Starting TorchTitan: {' '.join(command)}")
    subprocess.run(command, check=True)
    # subprocess.run(command, check=True, env=environment)

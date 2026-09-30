"""Pretrain a model with TorchTitan."""
from core.utils.files import folder_create

import os
import subprocess
from typing import Optional, no_type_check
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
    job_dir = os.path.abspath(os.path.join("jobs", args.model_name))  # torchtitan needs absolute paths
    output_dir = os.path.join(job_dir, "output")
    model_dir = download_model(args.model_name, os.path.join(job_dir, "assets"))

    # TODO: Download tokenizer if different from model

    dataset_name = os.path.splitext(os.path.basename(args.dataset.path))[0]
    dataset_path = os.path.join(job_dir, "datasets", f"{dataset_name}-{args.dataset.split}.jsonl")
    dataset_path = download_dataset(args.dataset.path, dataset_path, split=args.dataset.split)

    ### --- Training ---
    env = os.environ.copy()
    env["MODULE"] = f"configs.torchtitan.{args.module_name}"
    env["CONFIG"] = args.config_name
    env["DATA_FILES"] = dataset_path
    logger.debug(f"Set env var 'DATA_FILES' to {dataset_path}")
    env.setdefault("NGPU", "1")

    command = [
        "/torchtitan/run_train.sh",
        "--dump_folder",
        output_dir,
        "--hf_assets_path",
        model_dir,
        "--checkpointer.initial_load_path",
        model_dir,
        "--checkpointer.initial_load_in_hf",
    ]

    logger.info(f"Starting TorchTitan: {' '.join(command)}")
    run_cmd(command, streaming=True, env=env)
    logger.info("✅ TorchTitan pretraining completed successfully.")

    ### --- Push model ---
    # upload_model(model_dir, args.hf_push_repo)


@no_type_check
def get_torchtitan_recipe(**args):
    from torchtitan.components.checkpointer import CheckpointManager
    from torchtitan.components.data import (
        ConcatThenSplitPackingConfig,
        GrainDataLoader,
        HuggingFaceStreamingSource,
        SingleDatasetConfig,
    )
    from torchtitan.components.loss import ChunkedLossWrapper, CrossEntropyLoss
    from torchtitan.components.optimizer import default_adamw, LRSchedulersContainer
    from torchtitan.config import (
        CompileConfig,
        DebugConfig,
        ParallelismConfig,
        TrainingConfig,
    )
    from torchtitan.distributed.activation_checkpoint import SelectiveAC
    from torchtitan.hf_datasets.text_datasets import TextProcessor
    from torchtitan.models.common.config_utils import decoder_vocab_size
    from torchtitan.models.qwen3 import model_registry
    from torchtitan.observability.metrics import MetricsProcessor
    from torchtitan.observability.profiler import Profiler
    from torchtitan.trainer import Trainer

    def qwen3_balanced_600m(
        dataset_path: str,
        checkpoint_folder: str,
        tokenizer_folder: str,
        dump_folder: str = "/dump",
    ) -> Trainer.Config:
        """Balanced 600M Qwen3 CPT"""
        model_spec = model_registry("balanced-600M", seq_len=4096)
        return Trainer.Config(
            dump_folder=dump_folder,
            hf_assets_path=tokenizer_folder,  # "/path/to/local/tokenizer"
            model_spec=model_spec,
            loss=ChunkedLossWrapper.Config(
                loss_fn=CrossEntropyLoss.Config(
                    global_vocab_size=decoder_vocab_size(model_spec),
                ),
            ),
            dataloader=GrainDataLoader.Config(
                dataset=ConcatThenSplitPackingConfig(
                    dataset=SingleDatasetConfig(
                        source=HuggingFaceStreamingSource.Config(
                            path="json",
                            split="train",
                            load_dataset_kwargs={
                                "data_files": dataset_path,  # "/path/to/local/dataset/*.jsonl"
                            },
                        ),
                        processor=TextProcessor.Config(),
                    ),
                ),
                shuffle=True,
                seed=42,
            ),
            optimizer=default_adamw(
                lr=5e-5,
                eps=1e-8,
                weight_decay=0.01,
            ),
            lr_scheduler=LRSchedulersContainer.Config(
                warmup_steps=100,
                decay_ratio=0.25,
                decay_type="linear",
                min_lr_factor=0.1,
            ),
            training=TrainingConfig(
                num_tokens_per_microbatch_per_dp_rank=8 * 4096,
                num_tokens_per_train_step=512 * 4096,
                max_context_length=4096,
                max_norm=1.0,
                steps=2385,
                dtype="float32",
                mixed_precision_param="bfloat16",
                mixed_precision_reduce="float32",
            ),
            parallelism=ParallelismConfig(
                data_parallel_replicate_degree=1,
                data_parallel_shard_degree=-1,
                tensor_parallel_degree=1,
                pipeline_parallel_degree=1,
                context_parallel_degree=1,
            ),
            checkpointer=CheckpointManager.Config(
                folder="checkpoint",
                interval=795,
                export_dtype="float32",
                initial_load_path=checkpoint_folder,  # "/path/to/local/model_dir/checkpoint"
                initial_load_model_only=True,
            ),
            activation_checkpoint=SelectiveAC.Config(),
            compile=CompileConfig(components=["model", "loss"]),
            metrics=MetricsProcessor.Config(
                log_freq=10,
                enable_tensorboard=False,
                enable_wandb=False,
                disable_color_printing=False,
            ),
            debug=DebugConfig(
                seed=42,
                print_config=True,
            ),
            profiler=Profiler.Config(
                enable_profiling=False,
                save_traces_folder="profile_trace",
                profile_freq=10,
                enable_memory_snapshot=False,
                save_memory_snapshot_folder="memory_snapshot",
            ),
        )

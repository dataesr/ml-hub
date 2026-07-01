"""
Concrete pipeline configuration classes.

Each class encodes everything about one pipeline: metadata, the typed args
class, default cloud infrastructure, and default tracking config.  They are
the single source of truth — no YAML files needed.

To add a new pipeline:
  1. Add an args class in pipeline_args.py (if new args are needed).
  2. Add a new class here inheriting PipelineConfig.
  3. Register it in registry.py.
"""

from typing import List, Optional
from pydantic import Field
from core.cloud.constants import (
    CONFIGS_CONTAINER,
    DATASETS_CONTAINER,
    JOBS_CONTAINER,
    COMPLETIONS_CONTAINER,
    CONFIGS_VOLUME,
    DATASETS_VOLUME,
    JOBS_VOLUME,
    COMPLETIONS_VOLUME,
)
from core.cloud.schemas import CloudJobInfrastructure, CloudJobVolume
from core.tracking.schemas import TrackingConfig
from core.pipelines.schemas.base import PipelineConfig
from core.pipelines.schemas.args import (
    FinetuneArgs,
    FinetuneUnslothArgs,
    InferenceArgs,
    EvaluateArgs,
    AxolotlArgs,
)

_FINETUNE_VOLUMES: List[CloudJobVolume] = [
    CloudJobVolume(container=CONFIGS_CONTAINER, mount=CONFIGS_VOLUME),
    CloudJobVolume(container=DATASETS_CONTAINER, mount=DATASETS_VOLUME),
    CloudJobVolume(container=JOBS_CONTAINER, mount=JOBS_VOLUME, permission="RWD"),
]

_INFERENCE_VOLUMES: List[CloudJobVolume] = [
    CloudJobVolume(container=CONFIGS_CONTAINER, mount=CONFIGS_VOLUME),
    CloudJobVolume(container=DATASETS_CONTAINER, mount=DATASETS_VOLUME),
    CloudJobVolume(container=COMPLETIONS_CONTAINER, mount=COMPLETIONS_VOLUME, permission="RWD"),
]

_RUN_ENTRYPOINT_CMD = ["/run.sh", "run_entrypoint"]


class FinetuneCausalConfig(PipelineConfig):
    """Finetune a causal model with LoRA and BitsAndBytes 4-bit quantization."""

    pipeline: str = "finetune-causal"
    description: str = "Finetune a causal model with LoRA and BitsAndBytes 4-bit quantization"
    tags: List[str] = ["finetuning", "causallm", "transformers", "lora", "bitsandbytes"]
    entrypoint: str = "core.pipelines.entrypoints.finetune_causal:run"
    environment: str = "cloud"

    args: Optional[FinetuneArgs] = None
    cloud: CloudJobInfrastructure = Field(
        default=CloudJobInfrastructure(
            image="ghcr.io/dataesr/ml-hub/cuda-base:latest",
            name="finetune-causallm",
            command=_RUN_ENTRYPOINT_CMD,
            gpu=1,
            flavor="l4-1-gpu",
            volumes=_FINETUNE_VOLUMES,
        )
    )
    tracking: TrackingConfig = Field(default=TrackingConfig())


class FinetuneCausalUnslothConfig(PipelineConfig):
    """Finetune a causal model with Unsloth for optimized 4-bit training."""

    pipeline: str = "finetune-causal-unsloth"
    description: str = "Finetune a causal model with Unsloth for optimized 4-bit training"
    tags: List[str] = ["finetuning", "causallm", "transformers", "unsloth"]
    entrypoint: str = "core.pipelines.entrypoints.finetune_causal_unsloth:run"
    environment: str = "cloud"

    args: Optional[FinetuneUnslothArgs] = None
    cloud: CloudJobInfrastructure = Field(
        default=CloudJobInfrastructure(
            image="ghcr.io/dataesr/ml-hub/cuda-unsloth:latest",
            name="finetune-causallm",
            command=_RUN_ENTRYPOINT_CMD,
            gpu=1,
            flavor="l4-1-gpu",
            volumes=_FINETUNE_VOLUMES,
        )
    )
    tracking: TrackingConfig = Field(default=TrackingConfig())


class DatasetInferenceConfig(PipelineConfig):
    """Run batch inference on a dataset with a model using vLLM."""

    pipeline: str = "dataset-inference"
    description: str = "Run batch inference on a dataset with a model using vLLM"
    tags: List[str] = ["dataset", "inference", "vllm"]
    entrypoint: str = "core.pipelines.entrypoints.dataset_inference:run"
    environment: str = "cloud"

    args: Optional[InferenceArgs] = None
    cloud: CloudJobInfrastructure = Field(
        default=CloudJobInfrastructure(
            image="ghcr.io/dataesr/ml-hub/cuda-vllm:latest",
            name="dataset-inference",
            command=_RUN_ENTRYPOINT_CMD,
            gpu=1,
            flavor="l4-1-gpu",
            volumes=_INFERENCE_VOLUMES,
        )
    )
    tracking: TrackingConfig = Field(default=TrackingConfig())


class DatasetEvaluateConfig(PipelineConfig):
    """Evaluate completions from a dataset or file using MLflow scorers."""

    pipeline: str = "dataset-evaluate"
    description: str = "Evaluate completions from a dataset or file using MLflow scorers"
    tags: List[str] = ["dataset", "evaluate", "mlflow"]
    entrypoint: str = "core.pipelines.entrypoints.dataset_evaluate:run"
    environment: str = "local"

    args: Optional[EvaluateArgs] = None
    tracking: TrackingConfig = Field(default=TrackingConfig())


class FinetuneCausalAxolotlConfig(PipelineConfig):
    """Finetune a causal model with Axolotl (image-native entrypoint)."""

    pipeline: str = "finetune-causal-axolotl"
    description: str = "Finetune a causal model with Axolotl"
    tags: List[str] = ["finetuning", "causallm", "transformers", "axolotl"]
    entrypoint: Optional[str] = None  # the Docker image has its own ENTRYPOINT
    environment: str = "cloud"

    args: Optional[AxolotlArgs] = None
    cloud: CloudJobInfrastructure = Field(
        default=CloudJobInfrastructure(
            image="ghcr.io/dataesr/ml-hub/cuda-axolotl:latest",
            name="finetune-causal-axolotl",
            command=[],
            gpu=1,
            flavor="l4-1-gpu",
            volumes=_FINETUNE_VOLUMES,
        )
    )
    tracking: Optional[TrackingConfig] = None

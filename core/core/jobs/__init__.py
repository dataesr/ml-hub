from core.jobs.merge_adapters import MergeAdaptersArgs, run_merge_adapters
from core.jobs.sft import SFTArgs, run_sft
from core.common.ovh import (
    OVHConfig,
    OVHVolume,
    CONFIGS_CONTAINER,
    CONFIGS_VOLUME,
    DATASETS_CONTAINER,
    DATASETS_VOLUME,
    COMPLETIONS_CONTAINER,
    COMPLETIONS_VOLUME,
    JOBS_CONTAINER,
    JOBS_VOLUME,
)
from core.jobs.inference import InferenceArgs, run_inference
from core.common.mlflow import MLflowConfig, MLflowRun
from pydantic import Field
from core.jobs.base import BaseJob
from typing import Type, List
from core.jobs.evaluate import EvaluateArgs, run_evaluate
from core.utils.logger import get_logger

logger = get_logger(__name__)

class EvaluateJob(BaseJob[EvaluateArgs]):
    """Evaluate completions from a dataset or file using MLflow scorers."""

    name: str = "dataset-evaluate"
    description: str = "Evaluate completions from a dataset or file using MLflow scorers"
    tags: List[str] = ["dataset", "evaluate", "mlflow"]

    args: EvaluateArgs = Field(default_factory=EvaluateArgs)
    mlflow: MLflowConfig = Field(default=MLflowConfig())

    def run(self, mlf: MLflowRun):
        return run_evaluate(self.args, mlf)


class InferenceJob(BaseJob[InferenceArgs]):
    """Run batch inference on a dataset with a model using vLLM."""

    name: str = "dataset-inference"
    description: str = "Run batch inference on a dataset with a model using vLLM"
    tags: List[str] = ["dataset", "inference", "vllm"]

    args: InferenceArgs = Field(default_factory=InferenceArgs)
    ovh: OVHConfig = Field(
        default=OVHConfig(
            image="ghcr.io/dataesr/ml-hub/cuda-vllm:latest",
            command=["/run.sh", "jobs", "run", "dataset-inference"],
            name="dataset-inference",
            gpu=1,
            flavor="l4-1-gpu",
            volumes=[
                OVHVolume(container=CONFIGS_CONTAINER, mount=CONFIGS_VOLUME),
                OVHVolume(container=DATASETS_CONTAINER, mount=DATASETS_VOLUME),
                OVHVolume(container=COMPLETIONS_CONTAINER, mount=COMPLETIONS_VOLUME, permission="RWD"),
            ],
        )
    )
    mlflow: MLflowConfig = Field(default=MLflowConfig())

    def run(self, mlf: MLflowRun):
        return run_inference(self.args, mlf)


class MergeAdaptersJob(BaseJob[MergeAdaptersArgs]):
    """Merge adapters to a base model and save merged model"""

    name: str = "merge-adapters"
    description: str = "Merge adapters to a base model and save merged model"
    tags: List[str] = ["huggingface", "adapters", "merge"]

    args: MergeAdaptersArgs = Field(default_factory=MergeAdaptersArgs)
    ovh: OVHConfig = OVHConfig(
        image="ghcr.io/dataesr/ml-hub/cuda-base:latest",
        command=["/run.sh", "jobs", "run", "merge-adapters"],
        name="merge-adapters",
        gpu=1,
        flavor="l4-1-gpu",
        volumes=[OVHVolume(container=JOBS_CONTAINER, mount=JOBS_VOLUME, permission="RWD")],
    )

    def run(self, mlf: MLflowRun):
        return run_merge_adapters(self.args)


class SFTJob(BaseJob[SFTArgs]):
    name: str = "finetune-sft"
    description: str = "Finetune a model with sft + LoRA and BitsAndBytes 4-bit quantization"
    tags: List[str] = ["finetuning", "sft", "transformers", "lora", "bitsandbytes"]

    args: SFTArgs = Field(default_factory=SFTArgs)
    ovh: OVHConfig = Field(
        default=OVHConfig(
            image="ghcr.io/dataesr/ml-hub/cuda-base:latest",
            command=["/run.sh", "jobs", "run", "finetune-sft"],
            name="finetune-sft",
            gpu=1,
            flavor="l4-1-gpu",
            volumes=[
                OVHVolume(container=CONFIGS_CONTAINER, mount=CONFIGS_VOLUME),
                OVHVolume(container=DATASETS_CONTAINER, mount=DATASETS_VOLUME),
                OVHVolume(container=JOBS_CONTAINER, mount=JOBS_VOLUME, permission="RWD"),
            ],
        )
    )
    mlflow: MLflowConfig = Field(default=MLflowConfig())

    def run(self, mlf: MLflowRun):
        return run_sft(self.args, mlf)


JOBS = SFTJob | InferenceJob | EvaluateJob | MergeAdaptersJob

JOBS_REGISTRY: dict[str, Type[JOBS]] = {
    "finetune-sft": SFTJob,
    "dataset-inference": InferenceJob,
    "dataset-evaluate": EvaluateJob,
    "merge-adapters": MergeAdaptersJob,
}


def list_jobs() -> list[Type[JOBS]]:
    """Return a fresh default instance for every registered job."""
    return [cls for cls in JOBS_REGISTRY.values()]


def get_job(name: str) -> Type[JOBS]:
    """Return a fresh default instance for the named pipeline."""

    cls = JOBS_REGISTRY.get(name)
    if cls is None:
        raise KeyError(f"Job '{name}' not found. Available: {list(JOBS_REGISTRY.keys())}")
    return cls

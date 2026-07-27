import jsonref
from core.utils.misc import build_cls_with_defaults
from pydantic import Field, create_model
from typing import Any
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
from core.common.mlflow import MLflowConfig, MLflowRun
from core.jobs.base import BaseJob
from core.jobs.evaluate import EvaluateArgs, run_evaluate
from core.jobs.merge_adapters import MergeAdaptersArgs, run_merge_adapters
from core.jobs.inference_vllm import InferenceVLLMArgs, run_inference_vllm

# from core.jobs.inference_scw import InferenceSCWArgs, run_inference_scw
from core.jobs.sft import SFTArgs, run_sft
from core.utils.logger import get_logger

logger = get_logger(__name__)


class EvaluateJob(BaseJob[EvaluateArgs]):
    """Evaluate completions from a dataset or file using MLflow scorers."""

    name: str = "dataset-evaluate"
    description: str = "Evaluate completions from a dataset or file using MLflow scorers"
    tags: list[str] = ["dataset", "evaluate", "mlflow"]

    args: EvaluateArgs = Field(default_factory=EvaluateArgs)
    mlflow: MLflowConfig = Field(default=MLflowConfig())

    def run(self, mlf: MLflowRun):
        return run_evaluate(self.args, mlf)


class InferenceVLLMJob(BaseJob[InferenceVLLMArgs]):
    """Run batch inference on a dataset with a model using vLLM."""

    name: str = "dataset-inference"
    description: str = "Run batch inference on a dataset with a model using vLLM"
    tags: list[str] = ["dataset", "inference", "vllm"]

    args: InferenceVLLMArgs = Field(default_factory=InferenceVLLMArgs)
    ovh: OVHConfig = Field(
        default=OVHConfig(
            image="ghcr.io/dataesr/ml-hub/cuda-vllm:latest",
            command=["/run.sh", "jobs", "exec", "dataset-inference"],
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
        return run_inference_vllm(self.args, mlf)


class MergeAdaptersJob(BaseJob[MergeAdaptersArgs]):
    """Merge adapters to a base model and save merged model"""

    name: str = "merge-adapters"
    description: str = "Merge adapters to a base model and save merged model"
    tags: list[str] = ["huggingface", "adapters", "merge"]

    args: MergeAdaptersArgs = Field(default_factory=MergeAdaptersArgs)
    ovh: OVHConfig = OVHConfig(
        image="ghcr.io/dataesr/ml-hub/cuda-base:latest",
        command=["/run.sh", "jobs", "exec", "merge-adapters"],
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
    tags: list[str] = ["finetuning", "sft", "transformers", "lora", "bitsandbytes"]

    args: SFTArgs = Field(default_factory=SFTArgs)
    ovh: OVHConfig = Field(
        default=OVHConfig(
            image="ghcr.io/dataesr/ml-hub/cuda-base:latest",
            command=["/run.sh", "jobs", "exec", "finetune-sft"],
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


JOBS = SFTJob | InferenceVLLMJob | EvaluateJob | MergeAdaptersJob

JOBS_REGISTRY: dict[str, type[JOBS]] = {
    "finetune-sft": SFTJob,
    "dataset-inference-vllm": InferenceVLLMJob,
    "dataset-evaluate": EvaluateJob,
    "merge-adapters": MergeAdaptersJob,
}


def list_jobs() -> list[type[JOBS]]:
    """Return the class for every registered job."""

    return [cls for cls in JOBS_REGISTRY.values()]


def get_job(name: str) -> type[JOBS]:
    """Return the class of a named job."""

    cls = JOBS_REGISTRY.get(name)
    if cls is None:
        raise KeyError(f"Job '{name}' not found. Available: {list(JOBS_REGISTRY.keys())}")
    return cls


def get_job_schema(cls: type[JOBS]) -> dict[str, Any]:
    """
    Return a JSON Schema object describing the user-facing inputs:
    ``args`` (required), ``ovh`` and ``mlflow`` (optional overrides).
    """

    job_fields = cls.model_fields
    args_cls = job_fields.get("args").default_factory
    ovh_cfg = job_fields.get("ovh").default
    mlflow_cfg = job_fields.get("mlflow").default

    fields: dict[str, tuple[Any, Any]] = {
        "args": (args_cls, Field(title="Jobs arguments")),
    }
    if ovh_cfg is not None:
        ovh_cls = build_cls_with_defaults(OVHConfig, ovh_cfg, "OVH")
        fields["ovh"] = (ovh_cls, Field(title="OVH configuration", default=None))
    if mlflow_cfg is not None:
        mlflow_cls = build_cls_with_defaults(MLflowConfig, mlflow_cfg, "MLflow")
        fields["mlflow"] = (mlflow_cls, Field(title="MLflow configuration", default=None))

    inputs_cls = create_model("Inputs", **fields)
    schema = inputs_cls.model_json_schema(union_format="primitive_type_array")
    return jsonref.replace_refs(schema)

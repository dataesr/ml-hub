# jobs/registry.py
from enum import Enum


class PipelineType(str, Enum):
    FINETUNE_CAUSAL = "finetune_causal"
    EVAL_ENTITY = "eval_entity_extraction"
    INFERENCE_API = "inference_api"


METADATA = {
    PipelineType.FINETUNE_CAUSAL: {
        "script": "jobs/training/finetune_causal.py",
        "description": "Finetunes a Llama-style model",
        "docker_target": "cuda_unsloth",
    },
    # ...
}


def get_pipeline_names():
    return [e.value for e in PipelineType]

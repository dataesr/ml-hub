"""
Pipeline registry — maps pipeline names to their config classes.

To register a new pipeline, import its config class and add an entry to
``_PIPELINE_REGISTRY``.
"""

from typing import Dict, List, Type
from core.pipelines.schemas.base import PipelineConfig
from core.pipelines.schemas.pipeline import (
    FinetuneCausalConfig,
    FinetuneCausalUnslothConfig,
    DatasetInferenceConfig,
    DatasetEvaluateConfig,
    FinetuneCausalAxolotlConfig,
)
from core.utils.logger import get_logger

logger = get_logger(__name__)

_PIPELINE_REGISTRY: Dict[str, Type[PipelineConfig]] = {
    "finetune-causal": FinetuneCausalConfig,
    "finetune-causal-unsloth": FinetuneCausalUnslothConfig,
    "dataset-inference": DatasetInferenceConfig,
    "dataset-evaluate": DatasetEvaluateConfig,
    "finetune-causal-axolotl": FinetuneCausalAxolotlConfig,
}


def list_pipelines() -> List[PipelineConfig]:
    """Return a fresh default instance for every registered pipeline."""

    return [cls() for cls in _PIPELINE_REGISTRY.values()]


def get_pipeline(name: str) -> PipelineConfig:
    """Return a fresh default instance for the named pipeline."""

    cls = _PIPELINE_REGISTRY.get(name)
    if cls is None:
        raise KeyError(f"Pipeline '{name}' not found. Available: {list(_PIPELINE_REGISTRY.keys())}")
    return cls()

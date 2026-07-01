"""
Pipeline config loader for user-provided YAML override files.

User YAML format:
    pipeline: finetune-causal   # required — selects the config class
    args:
      model_name: mistralai/Mistral-7B-v0.3
      dataset:
        path: dataesr/my-dataset
      epochs: 5
    # Optional overrides for cloud / tracking:
    tracking:
      project_name: my-experiment
"""

from pathlib import Path
from typing import Any, Dict
from core.pipelines.schemas.base import PipelineConfig
from core.pipelines.registry import get_pipeline
from core.cloud.schemas import CloudJobInfrastructure
from core.tracking.schemas import TrackingConfig
from core.configs.load import deep_merge, load_yaml_config
from core.utils.logger import get_logger

logger = get_logger(__name__)


def load_user_config(
    path: str | Path,
    overrides: Dict[str, Any] = {},
) -> PipelineConfig:
    """
    Load a user YAML config that overrides a named pipeline's defaults.

    Steps:
      1. Parse the YAML file.
      2. Look up the pipeline by name to get a fresh config instance.
      3. Apply ``args:`` overrides (merged with any CLI *overrides*).
      4. Optionally override ``cloud:`` and ``tracking:`` sections.
    """

    data = load_yaml_config(str(path), from_disk=True)

    pipeline_name = data.get("pipeline")
    if not pipeline_name:
        raise ValueError(f"User config must specify a 'pipeline' field: {path}")

    cfg = get_pipeline(pipeline_name)

    # Merge args from YAML + CLI overrides
    user_args = data.get("args", {})
    if overrides:
        user_args = deep_merge(user_args, overrides)
    if user_args:
        cfg.update_args(user_args)

    # Optional cloud override
    if "cloud" in data:
        cfg.cloud = CloudJobInfrastructure.model_validate(
            deep_merge(cfg.cloud.model_dump() if cfg.cloud else {}, data["cloud"])
        )

    # Optional tracking override
    if "tracking" in data:
        cfg.tracking = TrackingConfig.model_validate(
            deep_merge(cfg.tracking.model_dump() if cfg.tracking else {}, data["tracking"])
        )

    logger.debug("Loaded user pipeline config: pipeline=%s from %s", pipeline_name, path)
    return cfg

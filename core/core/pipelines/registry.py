"""
Pipeline registry — scans YAML config files to discover pipelines.

Replaces the old decorator-based registry with a simple filesystem scan
of `pipelines/configs/*.yaml`.
"""

from typing import Dict, List
from core.pipelines.schemas import PipelineConfig
from core.pipelines.load import CONFIGS_DIR, load_pipeline_config
from core.utils.logger import get_logger

logger = get_logger(__name__)

# In-memory cache of loaded pipeline configs
_PIPELINE_REGISTRY: Dict[str, PipelineConfig] = {}


def _load_all_configs() -> None:
    """Scan the configs directory and load all pipeline YAML files."""
    global _PIPELINE_REGISTRY

    if not CONFIGS_DIR.exists():
        logger.warning(f"Pipeline configs directory not found: {CONFIGS_DIR}")
        return

    for yaml_file in sorted(CONFIGS_DIR.glob("*.yaml")):
        try:
            config = load_pipeline_config(yaml_file)
            _PIPELINE_REGISTRY[config.pipeline] = config
            logger.debug(f"Registered pipeline: {config.pipeline} (env={config.environment})")
            logger.debug(f"{config=}")
        except Exception as error:
            logger.warning(f"Failed to load pipeline config {yaml_file.name}: {error}")


def _ensure_loaded() -> None:
    """Lazy-load pipeline configs on first access."""
    if not _PIPELINE_REGISTRY:
        _load_all_configs()


def list_pipelines() -> List[PipelineConfig]:
    """Return all registered pipeline configs."""
    _ensure_loaded()
    return list(_PIPELINE_REGISTRY.values())


def get_pipeline(name: str) -> PipelineConfig:
    """Get a pipeline config by name."""
    _ensure_loaded()

    config = _PIPELINE_REGISTRY.get(name)
    if not config:
        raise KeyError(f"Pipeline '{name}' not found. Available: {list(_PIPELINE_REGISTRY.keys())}")

    return config


def reload_pipelines() -> None:
    """Force reload all pipeline configs from disk."""
    global _PIPELINE_REGISTRY
    _PIPELINE_REGISTRY = {}
    _load_all_configs()

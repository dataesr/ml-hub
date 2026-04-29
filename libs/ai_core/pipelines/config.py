from pathlib import Path
from typing import Any, Dict
from ai_core.pipelines.schemas import PipelineConfig
from ai_core.configs.load import deep_merge, load_yaml_config
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)

CONFIGS_DIR = Path(__file__).parent / "configs"


def resolve_base_config(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    If the config has a `base:` field, load the base pipeline config
    and deep-merge the user's overrides on top.
    """
    base_name = data.pop("base", None)
    if not base_name:
        return data

    # Find the base config in the built-in configs directory
    base_path = CONFIGS_DIR / f"{base_name}.yaml"
    if not base_path.exists():
        raise FileNotFoundError(f"Base pipeline config '{base_name}' not found at {base_path}")

    base_data = load_yaml_config(base_path.as_posix(), from_disk=True)
    # Recursively resolve (base configs can themselves have a base)
    base_data = resolve_base_config(base_data)

    # Deep merge: user overrides win
    merged = deep_merge(base_data, data)
    return merged


def load_pipeline_config(path: str | Path, overrides: Dict[str, Any] = {}) -> PipelineConfig:
    """
    Load a pipeline config from a YAML file path.
    Supports `base:` inheritance.
    """
    data = load_yaml_config(str(path), from_disk=True)
    data = resolve_base_config(data)

    config = PipelineConfig.model_validate(data)
    config = config.update_args(overrides)
    logger.debug(f"Loaded pipeline config: {config.pipeline}")
    return config


def load_pipeline_config_by_name(name: str) -> PipelineConfig:
    """Load a built-in pipeline config by its name."""
    path = CONFIGS_DIR / f"{name}.yaml"
    return load_pipeline_config(path)


def load_user_config(
    path: str | Path,
    overrides: Dict[str, Any] = {},
) -> PipelineConfig:
    """
    Load a user-provided config (which may use `base:` inheritance)
    and apply optional programmatic overrides.
    """
    user_data = load_yaml_config(str(path), from_disk=True)
    user_args = user_data.pop("args", {})
    if "base" not in user_data:
        raise ValueError(f"User config must specify a 'base' pipeline to inherit from: {path}")

    base_data = resolve_base_config(user_data)
    base_config = PipelineConfig.model_validate(base_data)  # validate base config first to ensure it's correct

    # Apply overrides
    if overrides:
        user_args = deep_merge(user_args, overrides)

    # Update user args on top of base config
    config = base_config.update_args(user_args)
    logger.debug(f"Loaded user pipeline config: {config.args.model_dump(exclude_unset=True)} from {path}")
    return config

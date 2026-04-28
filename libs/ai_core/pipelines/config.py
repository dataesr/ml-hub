from pathlib import Path
from typing import Any, Dict, Optional
from ai_core.pipelines.schemas import ArgField, PipelineConfig, _PYTHON_TYPE_MAP
from ai_core.configs.load import deep_merge, load_yaml_config
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)

CONFIGS_DIR = Path(__file__).parent / "configs"


def _parse_args_section(raw_args: Dict[str, Any]) -> Dict[str, ArgField | Dict[str, ArgField]]:
    """
    Parse the `args:` section from YAML into ArgField objects.

    Supports two formats:
    - Full: `{ type: str, default: "train", description: "..." }`
    - Short: just a scalar value treated as the default
    """
    parsed = {}
    for name, spec in raw_args.items():
        if isinstance(spec, dict):
            if "type" not in spec or not isinstance(spec["type"], str):
                parsed[name] = _parse_args_section(spec)
            else:
                # If 'required' not explicitly set, infer from 'default' key presence
                if "required" not in spec and "default" not in spec:
                    spec["required"] = True
                parsed[name] = ArgField(**spec)
        else:
            # Short-form: bare value is the default
            inferred_type = type(spec).__name__ if spec is not None else "str"
            if inferred_type not in _PYTHON_TYPE_MAP:
                inferred_type = "str"
            parsed[name] = ArgField(type=inferred_type, default=spec, required=False)
    return parsed


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


def load_pipeline_config(path: str | Path) -> PipelineConfig:
    """
    Load a pipeline config from a YAML file path.
    Supports `base:` inheritance.
    """
    data = load_yaml_config(path.as_posix(), from_disk=True)
    data = resolve_base_config(data)

    # Parse args section specially
    if "args" in data and isinstance(data["args"], dict):
        data["args"] = _parse_args_section(data["args"])

    config = PipelineConfig.model_validate(data)
    logger.debug(f"Loaded pipeline config: {config.pipeline}")
    return config


def load_pipeline_config_by_name(name: str) -> PipelineConfig:
    """Load a built-in pipeline config by its name."""
    path = CONFIGS_DIR / f"{name}.yaml"
    return load_pipeline_config(path)


def load_user_config(
    path: str | Path,
    overrides: Optional[Dict[str, Any]] = None,
) -> PipelineConfig:
    """
    Load a user-provided config (which may use `base:` inheritance)
    and apply optional programmatic overrides.
    """
    data = load_yaml_config(str(path), from_disk=True)
    data = resolve_base_config(data)

    # Apply overrides
    if overrides:
        if "args" in overrides:
            data.setdefault("args", {})
            data["args"] = deep_merge(data["args"], overrides.pop("args"))
        data = deep_merge(data, overrides)

    # Parse args section
    if "args" in data and isinstance(data["args"], dict):
        data["args"] = _parse_args_section(data["args"])

    config = PipelineConfig.model_validate(data)
    return config

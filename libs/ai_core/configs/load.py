import os
import yaml
from typing import Dict, Any
from ai_core.cloud.containers import CONFIGS_CONTAINER
from ai_core.cloud.storage import ovhai_object_download


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dicts. Override values take priority."""
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def load_yaml_config(cfg_name: str, cfg_type: str) -> Dict[str, Any]:
    remote_path = os.path.join(cfg_type, cfg_name)
    if not remote_path.endswith(".yaml"):
        remote_path += ".yaml"

    try:
        file_path = ovhai_object_download(remote_path, CONFIGS_CONTAINER, output="/tmp/")
    except Exception as error:
        raise Exception(f"Error while downloading config {remote_path} from {CONFIGS_CONTAINER} (details={error})")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Downloaded config {remote_path} not found on disk ({file_path=})")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            cfg = yaml.safe_load(file)
    except Exception as error:
        raise yaml.YAMLError(f"Error while parsing {file_path}")

    os.remove(file_path)
    return cfg


def load_prompt_config(cfg_name: str):
    cfg = load_yaml_config(cfg_name, "prompts")
    return cfg


def load_pipeline_config(cfg_name: str):
    cfg = load_yaml_config(cfg_name, "pipeline")
    return cfg


def load_config(
    *,
    prompt: str = None,
    pipeline: str = None,
    overrides: Dict[str, Any] = None,
) -> Dict:
    """Load config from remote storage

    Args:
        prompt (str, optional): Prompt config name.
        pipeline (str, optional): Pipeline config name.
        overrides (Dict[str, Any], optional): Override config fields.

    Returns:
        Dict: config
    """
    final_cfg = {}

    # Prompt config
    if prompt:
        prompt_cfg = load_prompt_config(prompt)
        final_cfg = prompt_cfg

    # Job pipeline config
    if pipeline:
        job_cfg = load_pipeline_config(pipeline)
        final_cfg = _deep_merge(final_cfg, job_cfg)

    # Overrides
    if overrides:
        final_cfg = _deep_merge(final_cfg, overrides)

    return final_cfg

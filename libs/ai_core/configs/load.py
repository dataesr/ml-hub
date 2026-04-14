import os
import yaml
from typing import Dict, Any
from ai_core.cloud.storage import ovhai_object_download
from ai_core.cloud.constants import CONFIGS_CONTAINER


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dicts. Override values take priority."""
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def load_yaml_config(path: str, from_disk: bool = False) -> Dict[str, Any]:
    if not path.endswith(".yaml"):
        path += ".yaml"

    if from_disk:
        file_path = path
    else:
        try:
            file_path = ovhai_object_download(path, CONFIGS_CONTAINER, output="/tmp/")
        except Exception as error:
            raise Exception(f"Error while downloading config {path} from {CONFIGS_CONTAINER} (details={error})")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Config {path} not found on disk ({file_path=})")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            cfg = yaml.safe_load(file)
    except Exception as error:
        raise yaml.YAMLError(f"Error while parsing {file_path}: {error}")

    if not from_disk:
        os.remove(file_path)
    return cfg

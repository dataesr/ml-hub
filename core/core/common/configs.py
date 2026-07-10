from core.utils.files import file_write_yaml
import os
import yaml
from typing import Any
from core.common.ovh import ovhai_object_download, CONFIGS_CONTAINER, ovhai_object_upload


def load_yaml_config(path: str, from_disk: bool = False) -> dict[str, Any]:
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


def write_yaml_config(cfg: dict, path: str):
    if not path.endswith(".yaml"):
        path += ".yaml"

    try:
        tmp_path = os.path.join("/tmp", path)
        file_write_yaml(tmp_path, cfg)
    except Exception as error:
        raise Exception(f"Error while writing config {path} as tmp file (details={error})")

    try:
        ovhai_object_upload(tmp_path, CONFIGS_CONTAINER, remove_prefix="/tmp/")
    except Exception as error:
        raise Exception(f"Error while uploading config {tmp_path} to {CONFIGS_CONTAINER} (details={error})")

    os.remove(tmp_path)
    return

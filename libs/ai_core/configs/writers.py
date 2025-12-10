import os
import yaml
from ai_core.cloud.containers import CONFIGS_CONTAINER
from ai_core.cloud.storage import ovhai_object_upload


def write_yaml_config(cfg: dict, cfg_name: str, cfg_folder: str):
    path = os.path.join(cfg_folder, cfg_name)
    if not path.endswith(".yaml"):
        path += ".yaml"

    try:
        tmp_path = os.path.join("tmp", path)
        with open(tmp_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(cfg, file, sort_keys=False)
    except Exception as error:
        raise Exception(f"Error while writing config {cfg_name} as tmp file (details={error})")

    try:
        ovhai_object_upload(tmp_path, CONFIGS_CONTAINER, remove_prefix="tmp/")
    except Exception as error:
        raise Exception(f"Error while uploading config {tmp_path} to {CONFIGS_CONTAINER}")
    os.remove(tmp_path)
    return


def write_prompt_config(cfg: dict, cfg_name: str):
    write_yaml_config(cfg, cfg_name, "prompts")


def write_pipeline_config(cfg: dict, cfg_name):
    write_yaml_config(cfg, cfg_name, "pipeline")

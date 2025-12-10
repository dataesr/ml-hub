import os
from ai_core.cloud.storage import ovhai_object_upload
from ai_core.utils.files import file_write_yaml
from ai_core.utils.logger import get_logger
from ai_core.schemas.constants import CONFIGS_CONTAINER

logger = get_logger(__name__)

def write_yaml_config(cfg: dict, cfg_name: str, cfg_type: str):
    path = os.path.join(cfg_type, cfg_name)
    if not path.endswith(".yaml"):
        path += ".yaml"

    try:
        tmp_path = os.path.join("/tmp", path)
        file_write_yaml(tmp_path, cfg)
    except Exception as error:
        raise Exception(f"Error while writing config {cfg_name} as tmp file (details={error})")

    try:
        ovhai_object_upload(tmp_path, CONFIGS_CONTAINER, remove_prefix="/tmp/")
    except Exception as error:
        raise Exception(f"Error while uploading config {tmp_path} to {CONFIGS_CONTAINER}")

    os.remove(tmp_path)
    return


def write_prompt_config(cfg: dict, cfg_name: str):
    write_yaml_config(cfg, cfg_name, "prompts")


def write_pipeline_config(cfg: dict, cfg_name):
    write_yaml_config(cfg, cfg_name, "pipeline")

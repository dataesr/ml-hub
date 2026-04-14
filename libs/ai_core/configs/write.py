import os
from ai_core.cloud.storage import ovhai_object_upload
from ai_core.cloud.constants import CONFIGS_CONTAINER
from ai_core.utils.files import file_write_yaml
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


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

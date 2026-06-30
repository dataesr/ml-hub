import os
from ai_core.cloud.client import ovhai_run_cmd
from ai_core.cloud.constants import CONTAINERS_REGION
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


def ovhai_object_list(container: str, prefix: str | None = None):
    cmd = ["ovhai", "bucket", "object", "list", f"{container}@{CONTAINERS_REGION}", "-o", "json"]
    if prefix:
        cmd.extend(["--prefix", prefix])
    data = ovhai_run_cmd(cmd, capture_json=True)
    return data


def ovhai_object_upload(object_name: str, container: str, prefix: str | None = None, remove_prefix: str | None = None):
    cmd = ["ovhai", "bucket", "object", "upload", f"{container}@{CONTAINERS_REGION}", object_name]
    if prefix:
        cmd.extend(["--add-prefix", prefix])
    if remove_prefix:
        cmd.extend(["--remove-prefix", remove_prefix])
    ovhai_run_cmd(cmd)


def ovhai_object_download(object_name: str, container: str, output: str | None = None, remove_prefix: str | None = None):
    output_path = object_name
    cmd = ["ovhai", "bucket", "object", "download", f"{container}@{CONTAINERS_REGION}", object_name]
    if remove_prefix:
        cmd.extend(["--remove-prefix", remove_prefix])
        output_path = output_path.removeprefix(remove_prefix)
    if output:
        cmd.extend(["--output", output])
        output_path = os.path.join(output, output_path)
    ovhai_run_cmd(cmd)
    return output_path


def ovhai_object_delete(container: str, object_name: str | None = None, prefix: str | None = None):
    cmd = ["ovhai", "bucket", "object", "delete", f"{container}@{CONTAINERS_REGION}"]
    if object_name:
        cmd.append(object_name)
    elif prefix:
        cmd.extend(["--prefix", prefix])
    else:
        cmd.append("--all")
    ovhai_run_cmd(cmd)

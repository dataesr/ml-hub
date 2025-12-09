import os
from ai_core.cloud.client import ovhai_run_cmd, DATA_STORE
from ai_core.logger import get_logger

logger = get_logger(__name__)


def ovhai_object_list(container: str, prefix: str = None):
    cmd = f"ovhai bucket object list {container}@{DATA_STORE} -o json"
    if prefix:
        cmd += f" --prefix {prefix}"
    data = ovhai_run_cmd(cmd, capture_json=True)
    return data


def ovhai_object_upload(object_name: str, container: str, prefix: str = None, remove_prefix: str = None):
    cmd = f"ovhai bucket object upload {container}@{DATA_STORE} {object_name}"
    if prefix:
        cmd += f" --add-prefix {prefix}"
    if remove_prefix:
        cmd += f" --remove-prefix {remove_prefix}"
    ovhai_run_cmd(cmd)


def ovhai_object_download(object_name: str, container: str, output: str = None, remove_prefix: str = None):
    output_path = object_name
    cmd = f"ovhai bucket object download {container}@{DATA_STORE} {object_name}"
    if remove_prefix:
        cmd += f" --remove-prefix {remove_prefix}"
        output_path = output_path.removeprefix(remove_prefix)
    if output:
        cmd += f" --output {output}"
        output_path = os.path.join(output, output_path)
    # logger.debug(f"{cmd =}")
    # logger.debug(f"{object_name=}, {output=}, {remove_prefix=}, {output_path=}")
    ovhai_run_cmd(cmd)
    return output_path


def ovhai_object_delete(container: str, object_name: str = None, prefix: str = None):
    to_delete = f"--all"
    if prefix:
        to_delete = f"--prefix {prefix}"
    if object_name:
        to_delete = object_name
    cmd = f"ovhai bucket object delete {container}@{DATA_STORE} {to_delete}"
    ovhai_run_cmd(cmd)

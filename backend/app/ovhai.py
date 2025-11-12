import os
import json
import subprocess
from app.logger import get_logger

logger = get_logger(__name__)

DATA_STORE = "1azgra"
CONTAINERS_PREFIX = "llm-"

def ovhai_initialize():
    # login
    cmd = f'ovhai login --username {os.getenv("OVHAI_USERNAME")} --password-from-env OVHAI_PASSWORD'
    result = subprocess.run(cmd, shell=True, text=True)
    result.check_returncode()

    # add s3 datastore
    cmd = f'ovhai datastore update s3 {DATA_STORE} {os.getenv("OVHAI_OS_ENDPOINT")} {os.getenv("OVHAI_OS_REGION").lower()} {os.getenv("OVHAI_OS_ACCESS_KEY")} --secret-key-from-env OVHAI_OS_SECRET_KEY --store-credentials-locally'
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    result.check_returncode()


def cmd_run(cmd: str, capture_json: bool = False):
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    # logger.debug(f"results {result.stdout}")
    if result.returncode != 0:
        # logger.error(f"CMD ERR: {result.stderr}")
        message = result.stderr or result.stdout
        raise Exception(f"CMD ERR: {message}")

    if result.returncode == 0 and capture_json:
        try:
            data: dict = json.loads(result.stdout)
            return data
        except Exception:
            # logger.error(f"Error while parsing json from {result.stdout}")
            raise ValueError(f"Error while parsing json from {result.stdout}")


def ovhai_object_list(container: str, prefix: str = None):
    cmd = f"ovhai bucket object list {container}@{DATA_STORE} -o json"
    if prefix:
        cmd += f" --prefix {prefix}"
    data = cmd_run(cmd, capture_json=True)
    return data


def ovhai_object_upload(object_name: str, container: str, prefix: str = None, remove_prefix: str = None):
    cmd = f"ovhai bucket object upload {container}@{DATA_STORE} {object_name}"
    if prefix:
        cmd += f" --add-prefix {prefix}"
    if remove_prefix:
        cmd += f" --remove-prefix {remove_prefix}"
    cmd_run(cmd)


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
    cmd_run(cmd)
    return output_path


def ovhai_object_delete(container: str, object_name: str = None, prefix: str = None):
    to_delete = f"--all"
    if prefix or object_name:
        to_delete = f"--prefix {prefix}" if prefix else object_name
    cmd = f"ovhai bucket object delete {container}@{DATA_STORE} {to_delete}"
    cmd_run(cmd)

import os
import json
import subprocess
from app.logger import get_logger

logger = get_logger(__name__)

DATA_STORE = "1azgra"

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

    if result.returncode != 0:
        logger.error(f"CMD ERR: {result.stderr}")
        raise Exception(f"CMD ERR: {result.stderr}")

    if result.returncode == 0 and capture_json:
        try:
            data: dict = json.loads(result.stdout)
            return data
        except Exception:
            logger.error(f"Error while parsing json from {result.stdout}")
            raise ValueError(f"Error while parsing json from {result.stdout}")


def ovhai_object_upload(file_path: str, container: str, prefix: str = None):
    cmd = f"ovhai bucket object upload {container}@{DATA_STORE} {file_path}"
    if prefix:
        cmd += f" --add-prefix {prefix}"
    cmd_run(cmd)


def ovhai_object_delete(object_name: str, container: str):
    cmd = f"ovhai bucket object delete {container}@{DATA_STORE}"
    cmd_run(cmd)


def ovhai_job_run(job_cli: str):
    cmd = f"ovhai job run -o json {job_cli}"
    data = cmd_run(cmd, capture_json=True)
    return data


def ovhai_job_stop(id: str):
    cmd = f"ovhai job stop {id}"
    cmd_run(cmd)


def ovhai_job_get(id: str):
    cmd = f"ovhai job get {id} -o json"
    data = cmd_run(cmd, capture_json=True)
    return data

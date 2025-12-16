import os
import json
import subprocess
from ai_core.cloud.constants import CONTAINERS_REGION

def ovhai_initialize():
    # login
    cmd = f'ovhai login --username {os.getenv("OVHAI_USERNAME")} --password-from-env OVHAI_PASSWORD'
    result = subprocess.run(cmd, shell=True, text=True)
    result.check_returncode()

    # add s3 datastore
    cmd = f'ovhai datastore update s3 {CONTAINERS_REGION} {os.getenv("OVHAI_OS_ENDPOINT")} {os.getenv("OVHAI_OS_REGION", "").lower()} {os.getenv("OVHAI_OS_ACCESS_KEY")} --secret-key-from-env OVHAI_OS_SECRET_KEY --store-credentials-locally'
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    result.check_returncode()


def ovhai_run_cmd(cmd: str, capture_json: bool = False):
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        message = result.stderr or result.stdout
        raise Exception(f"CMD ERR: {message}")

    if result.returncode == 0 and capture_json:
        try:
            data: dict = json.loads(result.stdout)
            return data
        except Exception:
            raise ValueError(f"Error while parsing json from {result.stdout}")

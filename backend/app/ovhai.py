import os
import json
import subprocess
from typing import Literal
from app.logger import get_logger

logger = get_logger(__name__)

JOB_STATE = Literal[
    "QUEUED",
    "PENDING",
    "INITIALIZING",
    "FINALIZING",
    "RUNNING",
    "TIMEOUT",
    "FAILED",
    "ERROR",
    "DONE",
    "INTERRUPTED",
    "INTERRUPTING",
    "SYNC_FAILED",
]

JOB_ACTIONS = Literal["GET", "STOP"]

def ovhai_initialize():
    cmd = f'ovhai login --username {os.getenv("OVHAI_USERNAME")} --password-from-env OVHAI_PASSWORD'
    result = subprocess.run(cmd, shell=True, text=True)
    result.check_returncode()


def cmd_get_data(cmd: str) -> dict:
    data = {}
    try:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        result.check_returncode()
        data = json.loads(result.stdout)
    except:
        logger.debug(f"error getting data for cmd {cmd}")
    return data


def ovhai_job_list(state: str = None):
    filter = f"-s {state}" if state else "-a"
    cmd = f"ovhai job list -o json {filter}"
    data = cmd_get_data(cmd)
    return data


def ovhai_job_run(job_cli: str):
    cmd = f"ovhai job run -o json {job_cli}"
    data = cmd_get_data(cmd)
    return data


def ovhai_job_stop(id: str):
    cmd = f"ovhai job stop {id}"
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    result.check_returncode()


def ovhai_job_get(id: str):
    cmd = f"ovhai job get {id} -o json"
    data = cmd_get_data(cmd)
    return data

import os
import json
import subprocess
from typing import Literal, Annotated
from fastapi import APIRouter, File, HTTPException
from app.logger import get_logger
from app.ovhai_finetuning import JOB as JOB_FT

logger = get_logger(__name__)

router = APIRouter(prefix="/ovhai")

DATA_STORE = "1azgra"

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


@router.get("/objects/{container}")
def objects_list(container: str):
    cmd = f"ovhai bucket object list -o json {container}@{DATA_STORE}"
    try:
        data = cmd_run(cmd, capture_json=True)
        return data
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/objects/upload_json")
def objects_upload_json(content: dict, file_path: str, container: str, prefix: str = None):
    tmp_path = f"/tmp/{file_path}"
    if not tmp_path.endswith(".json"):
        tmp_path += ".json"
    with open(tmp_path, "w") as f:
        json.dump(content, f)
    try:
        ovhai_object_upload(tmp_path, container, prefix)
        os.remove(tmp_path)
        return {f"{file_path}": "uploaded"}
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/objects/delete")
def objects_delete(object_name: str, container: str):
    try:
        ovhai_object_delete(object_name, container)
        return {f"{object_name}": "deleted"}
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/jobs")
def jobs_list(state: JOB_STATE = None):
    filter = f"-s {state}" if state else "-a"
    cmd = f"ovhai job list -o json {filter}"
    try:
        data = cmd_run(cmd, capture_json=True)
        return data
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/jobs/{id}")
async def jobs_action(id: str, action: JOB_ACTIONS = "GET"):
    try:
        if action == "GET":
            data = ovhai_job_get(id)
            return data
        if action == "STOP":
            ovhai_job_stop(id)
            return {f"{id}": "stopped"}
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/jobs/finetuning")
async def jobs_finetune(job: JOB_FT):
    try:
        data = ovhai_job_run(job.get_cli())
        return data
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

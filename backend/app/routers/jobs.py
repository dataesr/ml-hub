from typing import Literal
from fastapi import APIRouter, HTTPException
from app.finetuning import JOB as JOB_FINETUNING
from app.ovhai import cmd_run, ovhai_job_get, ovhai_job_run, ovhai_job_stop

router = APIRouter()

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
async def jobs_finetune(job: JOB_FINETUNING):
    try:
        data = ovhai_job_run(job.get_cli())
        return data
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

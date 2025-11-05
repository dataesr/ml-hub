from fastapi import APIRouter, HTTPException
from app.jobs.schemas import JOB_INPUTS, JOB_STATE
import app.jobs.service as jobs_svc

router = APIRouter()


@router.get("/jobs")
def jobs_list(state: JOB_STATE = None):
    try:
        jobs = jobs_svc.list(state)
        return jobs
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/jobs/{id}")
def jobs_get(id: str):
    try:
        job = jobs_svc.get(id)
        return job
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/jobs")
def jobs_run(job_inputs: JOB_INPUTS):
    try:
        job = jobs_svc.run(job_inputs)
        return job
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/jobs/{id}/stop")
def jobs_stop(id: str):
    try:
        jobs_svc.stop(id)
        return {f"{id}": "stopped"}
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))

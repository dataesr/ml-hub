from fastapi import APIRouter, HTTPException
from app.jobs.schemas import JOB_INPUTS, JOB_STATE
import app.jobs.service as jobs_svc

router = APIRouter()


@router.get("/jobs")
def jobs_list(state: JOB_STATE = None):
    jobs = jobs_svc.get_all(state)
    return jobs


@router.post("/jobs")
def jobs_run(job_inputs: JOB_INPUTS):
    job = jobs_svc.run(job_inputs)
    return job


@router.get("/jobs/{id}")
def jobs_get(id: str):
    job = jobs_svc.get(id)
    return job


@router.post("/jobs/{id}/stop")
def jobs_stop(id: str):
    jobs_svc.stop(id)
    return {f"{id}": "stopped"}

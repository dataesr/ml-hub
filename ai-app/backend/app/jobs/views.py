from fastapi import APIRouter
from app.jobs.schemas import TRAIN_INPUTS, INFERE_INPUTS, JOB_STATE
import app.jobs.service as jobs_svc

router = APIRouter(tags=["jobs"])


@router.get("/jobs")
def jobs_list(state: JOB_STATE = None):
    jobs = jobs_svc.get_all(state)
    return jobs


@router.post("/jobs/train")
def jobs_train(job_inputs: TRAIN_INPUTS):
    job = jobs_svc.run_train(job_inputs)
    return job


@router.post("/jobs/infere")
def jobs_infere(job_inputs: INFERE_INPUTS):
    job = jobs_svc.run_infere(job_inputs)
    return job


@router.get("/jobs/{id}")
def jobs_get(id: str):
    job = jobs_svc.get(id)
    return job


@router.post("/jobs/{id}/stop")
def jobs_stop(id: str):
    jobs_svc.stop(id)
    return {f"{id}": "stopped"}

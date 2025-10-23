from fastapi import APIRouter
from app.hf import hf_list_models, hf_model_info
from backend.app.ovhai import ovhai_job_get, ovhai_job_run, ovhai_job_stop
from backend.app.ovhai_finetuning import JOB as FT_JOB

router = APIRouter()


### huggingface hub
@router.get("/model/{owner}/{name}")
async def hf_get_model(owner: str, name: str):
    model = hf_model_info(f"{owner}/{name}")
    return model


@router.get("/models/{owner}")
async def hf_get_models(owner: str):
    models = hf_list_models(owner)
    return models


### ovhai - jobs
@router.get("/ovhai/jobs/{id}")
async def get_job(id: str):
    data = ovhai_job_get(id)
    return data


@router.get("/ovhai/jobs/{id}/stop")
async def stop_job(id: str):
    ovhai_job_stop(id)
    return {"message": "ok"}


### ovhai - finetuning
@router.post("/ovhai/jobs")
async def create_ft_job(job: FT_JOB):
    data = ovhai_job_run(job.get_cli())
    return data

from fastapi import APIRouter
from app.hf import hf_list_models, hf_model_info
from app.ovhai import JOB_ACTIONS, ovhai_job_get, ovhai_job_list, ovhai_job_run, ovhai_job_stop
from app.ovhai import JOB_STATE
from app.ovhai_finetuning import JOB as JOB_FT

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
@router.get("/ovhai/jobs")
async def get_jobs(state: JOB_STATE = None):
    data = ovhai_job_list(state)
    return data


@router.get("/ovhai/jobs/{id}")
async def manage_job(id: str, action: JOB_ACTIONS = "GET"):
    if action == "GET":
        data = ovhai_job_get(id)
        return data
    if action == "STOP":
        try:
            ovhai_job_stop(id)
            return {"message": "ok"}
        except Exception as error:
            return {"error": error.stderr}


### ovhai - finetuning
@router.post("/finetune")
async def create_ft_job(job: JOB_FT):
    data = ovhai_job_run(job.get_cli())
    return data

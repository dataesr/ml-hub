from fastapi import APIRouter, HTTPException
from app.hf import hf_dataset_info, hf_list_datasets, hf_list_models, hf_model_info
from app.ovhai import JOB_ACTIONS, ovhai_job_get, ovhai_job_list, ovhai_job_run, ovhai_job_stop
from app.ovhai import JOB_STATE
from app.ovhai_finetuning import JOB as JOB_FT
from app.wandb import RUN_STATES, wandb_list_projects, wandb_list_runs

router = APIRouter()


### huggingface hub
@router.get("/hf/dataset/{owner}/{name}")
async def hf_get_dataset(owner: str, name: str):
    try:
        dataset = hf_dataset_info(f"{owner}/{name}")
        return dataset
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/hf/datasets/{owner}")
async def hf_get_datasets(owner: str):
    datasets = hf_list_datasets({owner})
    return datasets


@router.get("/hf/model/{owner}/{name}")
async def hf_get_model(owner: str, name: str):
    try:
        model = hf_model_info(f"{owner}/{name}")
        return model
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/hf/models/{owner}")
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


@router.post("/ovhai/jobs/finetuning")
async def create_ft_job(job: JOB_FT):
    data = ovhai_job_run(job.get_cli())
    return data


### Weight & Biases
@router.get("/wandb/projects/{entity}")
async def get_projects(entity: str):
    data = wandb_list_projects(entity)
    return data


@router.get("/wandb/runs/{entity}/{project}")
async def get_runs(entity: str, project: str, state: RUN_STATES = None):
    data = wandb_list_runs(entity, project, state)
    return data

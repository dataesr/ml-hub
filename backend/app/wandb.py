from typing import Literal
from fastapi import APIRouter
import wandb
from wandb import Api as wb
from app.logger import get_logger

logger = get_logger(__name__)

RUN_STATES = Literal["crashed", "failed", "finished", "killed", "running", "pending"]
ARTIFACT_TYPES = Literal["model", "dataset"]

router = APIRouter(prefix="/wandb")

wb = wandb.Api()


@router.get("/projects/{entity}")
def wandb_list_projects(entity: str):
    projects = wb.projects(entity=entity)
    projects = [project._attrs for project in projects]
    return projects


@router.get("/projects/{entity}/{project}")
def wandb_get_project(entity: str, project: str):
    project = wb.project(name=project, entity=entity)
    return project._attrs


@router.get("/runs/{entity}/{project}")
def wandb_list_runs(entity: str, project: str, state: RUN_STATES = None):
    runs = wb.runs(f"{entity}/{project}")
    runs = [
        {
            "id": run.id,
            "name": run.name,
            "displayName": run.displayName,
            "state": run.state,
            "createdAt": run.createAt,
            "url": run.url,
        }
        for run in runs
    ]
    if state:
        runs = [run for run in runs if run["state"] == state]
    return runs


@router.get("/runs/{entity}/{project}/{id}")
def wandb_get_run(entity: str, project: str, id: str):
    run = wb.run(path=f"{entity}/{project}/{id}")
    return run._attrs


@router.get("/artifacts/{entity}/{project}/{type}")
def wandb_list_artifacts(entity: str, project: str, type: ARTIFACT_TYPES):
    artifacts = wb.artifact_collections(project_name=f"{entity}/{project}", type_name=type)
    artifacts = [artifact._attrs for artifact in artifacts]
    return artifacts


@router.get("/artifacts/{entity}/{project}/{type}/{name}")
def wandb_get_artifact(entity: str, project: str, name: str, type: ARTIFACT_TYPES):
    artifact = wb.artifact(name=f"{entity}/{project}/{name}", type=type)
    return artifact._attrs

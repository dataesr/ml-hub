from fastapi import APIRouter
import app.experiments.service as exp_svc
from app.experiments.schemas import ARTIFACT_TYPES, RUN_STATES

router = APIRouter()


@router.get("/experiments")
def experiments_projects_list():
    projects = exp_svc.list_projects()
    return projects


@router.get("/experiments/{project}")
def experiments_projects_get(project: str):
    project = exp_svc.get_project(project)
    return project


@router.get("/experiments/runs/{project}")
def experiments_runs_list(project: str, state: RUN_STATES = None):
    runs = exp_svc.list_runs(project, state)
    return runs


@router.get("/experiments/runs/{project}/{id}")
def experiments_runs_get(project: str, id: str):
    run = exp_svc.get_run(project, id)
    return run


@router.get("/experiments/artifacts/{project}")
def experiments_artifacts_list(project: str, type: ARTIFACT_TYPES = "model"):
    artifacts = exp_svc.list_artifacts(project, type)
    return artifacts


@router.get("/experiments/artifacts/{project}/{name}")
def experiments_artifacts_get(project: str, name: str, type: ARTIFACT_TYPES = "model"):
    artifact = exp_svc.get_artifact(project, name, type)
    return artifact

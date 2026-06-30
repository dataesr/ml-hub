from fastapi import APIRouter
import app.services.experiments as exp_svc

router = APIRouter(tags=["experiments"])


@router.get("/experiments")
def experiments_projects_list():
    projects = exp_svc.get_all()
    return projects


@router.get("/experiments/{id}")
def experiments_projects_get(id: str):
    project = exp_svc.get(id)
    return project


@router.get("/experiments/{id}/runs")
def experiments_runs_list(id: str, state: str | None = None):
    runs = exp_svc.list_runs(id, state)
    return runs


@router.get("/experiments/runs/{run_id}")
def experiments_runs_get(run_id: str):
    run = exp_svc.get_run(run_id)
    return run

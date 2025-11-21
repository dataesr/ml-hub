import os
from mlflow import MlflowClient
from mlflow.entities import RunStatus
from app.logger import get_logger

logger = get_logger(__name__)

client = MlflowClient(tracking_uri=os.getenv("MLFLOW_TRACKING_URI"))
logger.debug(f"client_tracking_uri = {client.tracking_uri}")


def get_all():
    projects = client.search_experiments(view_type="ALL")
    projects = [
        {
            "id": project.experiment_id,
            "name": project.name,
            "created_at": project.creation_time,
            "updated_at": project.last_update_time,
            "tags": project.tags,
        }
        for project in projects
    ]
    return projects


def get(id: str):
    project = client.get_experiment(experiment_id=id)
    return project.__dict__


def list_runs(id: str, state: RunStatus = None):
    runs = client.search_runs(experiment_ids=[id])
    runs = [run.info.__dict__ for run in runs]
    if state:
        runs = [run for run in runs if run["status"] == state]
    return runs


def get_run(run_id: str):
    run = client.get_run(run_id=run_id)
    return run.__dict__

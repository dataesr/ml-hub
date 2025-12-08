import os
from mlflow import MlflowClient
from mlflow.entities import RunStatus
from app.logger import get_logger

logger = get_logger(__name__)

client = MlflowClient(tracking_uri=os.getenv("MLFLOW_TRACKING_URI"))
logger.debug(f"client_tracking_uri = {client.tracking_uri}")


def get_all():
    projects = client.search_experiments(view_type="ACTIVE_ONLY")
    projects = [
        {
            "id": project.experiment_id,
            "name": project.name,
            "created_at": project.creation_time,
            "updated_at": project.last_update_time,
            "tags": project.tags,
            "runs": len(client.search_runs(experiment_ids=[project.experiment_id])),
            "external_url": f"{client.tracking_uri}/#/experiments/{project.experiment_id}/runs",
        }
        for project in projects
    ]
    return projects


def get(id: str):
    project = client.get_experiment(experiment_id=id)
    project = {
        "id": project.experiment_id,
        "name": project.name,
        "created_at": project.creation_time,
        "updated_at": project.last_update_time,
        "tags": project.tags,
        "external_url": f"{client.tracking_uri}/#/experiments/{project.experiment_id}/runs",
    }
    return project


def list_runs(id: str, state: RunStatus = None):
    runs = client.search_runs(experiment_ids=[id])
    runs = [
        {
            "id": run.info.run_id,
            "name": run.info.run_name,
            "status": run.info.status,
            "experiment_id": run.info.experiment_id,
            "user_id": run.info.user_id,
            "start_time": run.info.start_time,
            "end_time": run.info.end_time,
            "tags": run.data.tags,
            "external_url": f"{client.tracking_uri}/#/experiments/{run.info.experiment_id}/runs/{run.info.run_id}",
        }
        for run in runs
    ]
    if state:
        runs = [run for run in runs if run["status"] == state]
    return runs


def get_run(run_id: str):
    run = client.get_run(run_id=run_id)
    run = {
        "id": run.info.run_id,
        "name": run.info.run_name,
        "status": run.info.status,
        "experiment_id": run.info.experiment_id,
        "user_id": run.info.user_id,
        "start_time": run.info.start_time,
        "end_time": run.info.end_time,
        "metrics": run.data.metrics,
        "params": run.data.params,
        "tags": run.data.tags,
        "external_url": f"{client.tracking_uri}/#/experiments/{run.info.experiment_id}/runs/{run.info.run_id}",
    }
    return run


def list_registered_models():
    models = client.search_registered_models()
    models = [model.__dict__ for model in models]
    return models


def list_logged_models():
    models = client.search_logged_models(experiment_ids=["4"])
    models = [model.to_dictionary() for model in models]
    return models


def list_datasets():
    ds = client.search_datasets(experiment_ids=["4"])
    ds = [d.to_dict() for d in ds]
    return ds

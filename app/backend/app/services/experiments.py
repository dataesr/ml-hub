from core.common.mlflow import mlflow_get_client
from core.utils.logger import get_logger

logger = get_logger(__name__)


def get_all():
    client = mlflow_get_client()
    if not client:
        return []
    projects = client.search_experiments(view_type="ACTIVE_ONLY")  # ty:ignore[invalid-argument-type]
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
    client = mlflow_get_client()
    if not client:
        return {}
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


def list_runs(id: str, state: str | None = None):
    client = mlflow_get_client()
    if not client:
        return []
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
    client = mlflow_get_client()
    if not client:
        return {}
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

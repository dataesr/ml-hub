import os
from fastapi import APIRouter
from core.cloud.constants import APP_STATE, JOB_STATE
from core.cloud.compute import (
    job_list,
    job_get,
    job_stop,
    app_list,
    app_get,
    app_start,
    app_stop,
    app_update_env,
)

router = APIRouter(prefix="/cloud", tags=["cloud", "jobs", "apps"])


## Utils
def _build_job_info(data: dict):
    infos = {
        "id": data["id"],
        "name": data["spec"]["name"],
        "task": data["spec"]["image"].split("/")[-1].split(":")[0],
        "state": data["status"]["state"],
        "created_at": data.get("createdAt"),
        "updated_at": data.get("updatedAt"),
        "queued_at": data["status"].get("queuedAt"),
        "started_at": data["status"].get("startedAt"),
        "stopped_at": data["status"].get("stoppedAt"),
        "finalized_at": data["status"].get("finalizedAt"),
        "duration": data["status"].get("duration"),
        "url": data["status"].get("url"),
        "external_url": f'{os.getenv("OVHAI_URL", "")}/training/{data["id"]}',
        "image": data["spec"]["image"],
        "resources": data["spec"]["resources"],
        "labels": data["spec"]["labels"],
    }
    return infos


def _build_app_info(data: dict):
    data["external_url"] = f'{os.getenv("OVHAI_URL", "")}/deploy/{data["id"]}'
    return data


# --- Cloud jobs ---
@router.get("/jobs")
def jobs_list(state: JOB_STATE | None = None):
    jobs = job_list(state)
    jobs = [_build_job_info(job) for job in jobs]
    return jobs


@router.get("/jobs/{id}")
def jobs_get(id: str):
    job = job_get(id)
    return _build_job_info(job)


@router.post("/jobs/{id}/stop")
def jobs_stop(id: str):
    job_stop(id)
    return {f"{id}": "stopped"}


# --- Cloud apps ---
@router.get("/apps")
def apps_list(state: APP_STATE | None = None):
    data = app_list(state)
    apps = [_build_app_info(app) for app in data]
    return apps


@router.get("/apps/{id}")
def apps_get(id: str):
    app = app_get(id)
    return _build_app_info(app)


@router.post("/apps/{id}/start")
def apps_start(id: str, model_name: str | None = None):
    if model_name:
        app_update_env(id, env_name="MODEL_NAME", env_value=model_name)
    app_start(id)
    return {f"{id}": "started"}


@router.post("/apps/{id}/stop")
def apps_stop(id: str):
    app_stop(id)
    return {f"{id}": "stopped"}

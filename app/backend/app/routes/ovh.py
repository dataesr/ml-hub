import os
from fastapi import APIRouter
from core.common.ovh import JOB_STATE, job_list, job_get, job_stop

router = APIRouter(prefix="/ovh", tags=["ovh", "jobs"])


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

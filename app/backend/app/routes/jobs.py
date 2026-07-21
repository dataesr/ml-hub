from core.utils.misc import deep_merge
from core.jobs import list_jobs, get_job
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["jobs"])


@router.get("/jobs")
def jobs_list():
    jobs_cls = list_jobs()
    jobs_fields = [cls.model_fields for cls in jobs_cls]
    logger.debug(f"jobs={jobs_fields}")
    return [
        {
            "name": job_fields.get("name").default,
            "description": job_fields.get("description").default,
            "tags": job_fields.get("tags").default,
            # "args": cfg.get("args").annotation,
            "ovh": job_fields.get("ovh").default,
            "mlflow": job_fields.get("mlflow").default,
            # "inputs": cfg.get_schema(),
            # "ovh": cfg.ovh.model_dump(exclude_unset=True) if cfg.ovh else None,
            # "mlflow": cfg.mlflow.model_dump(exclude_unset=True) if cfg.mlflow else None,
        }
        for job_fields in jobs_fields
    ]


@router.get("/jobs/{job_name}")
def jobs_get(job_name: str):
    try:
        job_fields = get_job(job_name).model_fields
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Job '{job_name}' not found.")

    return {
        "name": job_fields.get("name").default,
        "description": job_fields.get("description").default,
        "tags": job_fields.get("tags").default,
        # # "inputs": cfg.get_schema(),
        # "args": cfg.args.model_dump() if cfg.args is not None else {},
        "ovh": job_fields.get("ovh").default,
        "mlflow": job_fields.get("mlflow").default,
    }


@router.post("/jobs/{job_name}/run")
def jobs_run_or_submit(job_name: str, raw_input_data: dict):
    try:
        job_cls = get_job(job_name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Pipeline '{job_name}' not found.")

    try:
        logger.info(f"Starting job '{job_name}' execution...")
        input_data = raw_input_data
        if "ovh" in raw_input_data and job_cls.ovh:
            input_data["ovh"] = deep_merge(job_cls.ovh.model_dump(), raw_input_data["ovh"])
        if "mlflow" in raw_input_data and job_cls.mlflow:
            input_data["mlflow"] = deep_merge(job_cls.mlflow.model_dump(), raw_input_data["mlflow"])
        job = job_cls.model_validate(input_data)
        results = job.submit(exec=True)
        logger.info(f"Job '{job_name}' completed with results: {results}")
    except ValidationError as error:
        raise HTTPException(status_code=422, detail=error.errors())
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    return {f"{job_name}": "ok"}

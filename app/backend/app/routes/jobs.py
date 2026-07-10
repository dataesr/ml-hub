from core.common.mlflow import MLflowConfig
from core.common.ovh import OVHConfig
from core.jobs import list_jobs, get_job
from core.utils.misc import deep_merge
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["jobs"])


@router.get("/jobs")
def jobs_list():
    jobs = list_jobs()
    jobs = [cfg.model_fields for cfg in jobs]
    logger.debug(f"jobs={jobs}")
    return [
        {
            "name": cfg.get("name").default,
            "description": cfg.get("description").default,
            "tags": cfg.get("tags").default,
            # "args": cfg.get("args").annotation,
            "ovh": cfg.get("ovh").default,
            "mlflow": cfg.get("mlflow").default,
            # "inputs": cfg.get_schema(),
            # "ovh": cfg.ovh.model_dump(exclude_unset=True) if cfg.ovh else None,
            # "mlflow": cfg.mlflow.model_dump(exclude_unset=True) if cfg.mlflow else None,
        }
        for cfg in jobs
    ]


@router.get("/jobs/{job_name}")
def jobs_get(job_name: str):
    try:
        cfg = get_job(job_name).model_fields
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Job '{job_name}' not found.")

    return {
        "name": cfg.get("name").default,
        "description": cfg.get("description").default,
        "tags": cfg.get("tags").default,
        # # "inputs": cfg.get_schema(),
        # "args": cfg.args.model_dump() if cfg.args is not None else {},
        "ovh": cfg.get("ovh").default,
        "mlflow": cfg.get("mlflow").default,
    }


@router.post("/jobs/{job_name}/run")
def jobs_run_or_submit(job_name: str, raw_input_data: dict):
    try:
        job = get_job(job_name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Pipeline '{job_name}' not found.")

    try:
        logger.info(f"Starting job '{job_name}' execution...")
        input_data = {"args": raw_input_data.get("args", {})}
        cfg = job.model_validate(input_data)
        # Apply optional cloud/tracking overrides from the request body
        if "ovh" in raw_input_data and cfg.ovh:
            cfg.ovh = OVHConfig.model_validate(deep_merge(cfg.ovh.model_dump(), raw_input_data["ovh"]))
        if "mlflow" in raw_input_data and cfg.mlflow:
            cfg.mlflow = MLflowConfig.model_validate(deep_merge(cfg.mlflow.model_dump(), raw_input_data["tracking"]))
        results = cfg.submit(exec=True)
        logger.info(f"Job '{job_name}' completed with results: {results}")
    except ValidationError as error:
        raise HTTPException(status_code=422, detail=error.errors())
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    return {f"{job_name}": "ok"}

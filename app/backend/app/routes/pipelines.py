from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from core.pipelines.registry import list_pipelines, get_pipeline
from core.pipelines.executor import exec_pipeline
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["pipelines"])


@router.get("/pipelines")
def pipelines_list():
    pipelines = list_pipelines()
    pipelines.sort(key=lambda x: x.pipeline)
    return [
        {
            "pipeline": cfg.pipeline,
            "description": cfg.description,
            "tags": cfg.tags,
            "environment": cfg.environment,
            # "entrypoint": cfg.entrypoint,
            "args": cfg.args.model_dump() if cfg.args is not None else {},
            # "inputs": cfg.get_schema(),
            "cloud": cfg.cloud.model_dump(exclude_unset=True) if cfg.cloud else None,
            "tracking": cfg.tracking.model_dump(exclude_unset=True) if cfg.tracking else None,
        }
        for cfg in pipelines
    ]


@router.get("/pipelines/{pipeline_name}")
def pipelines_get(pipeline_name: str):
    try:
        cfg = get_pipeline(pipeline_name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Pipeline '{pipeline_name}' not found.")

    return {
        "pipeline": cfg.pipeline,
        "description": cfg.description,
        "tags": cfg.tags,
        "environment": cfg.environment,
        "entrypoint": cfg.entrypoint,
        "inputs": cfg.get_schema(),
        "cloud": cfg.cloud.model_dump() if cfg.cloud else None,
        "tracking": cfg.tracking.model_dump() if cfg.tracking else None,
    }


@router.post("/pipelines/{pipeline_name}/run")
def pipelines_run(pipeline_name: str, raw_input_data: dict):
    try:
        cfg = get_pipeline(pipeline_name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Pipeline '{pipeline_name}' not found.")

    try:
        logger.info(f"Starting pipeline '{pipeline_name}' execution...")
        cfg.update_args(raw_input_data.get("args", {}))
        # Apply optional cloud/tracking overrides from the request body
        if "cloud" in raw_input_data and cfg.cloud:
            from core.configs.load import deep_merge
            from core.cloud.schemas import CloudJobInfrastructure
            cfg.cloud = CloudJobInfrastructure.model_validate(
                deep_merge(cfg.cloud.model_dump(), raw_input_data["cloud"])
            )
        if "tracking" in raw_input_data and cfg.tracking:
            from core.configs.load import deep_merge
            from core.tracking.schemas import TrackingConfig
            cfg.tracking = TrackingConfig.model_validate(
                deep_merge(cfg.tracking.model_dump(), raw_input_data["tracking"])
            )
        results = exec_pipeline(cfg)
        logger.info(f"Pipeline '{pipeline_name}' completed with results: {results}")
    except ValidationError as error:
        raise HTTPException(status_code=422, detail=error.errors())
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    return {f"{pipeline_name}": "ok"}

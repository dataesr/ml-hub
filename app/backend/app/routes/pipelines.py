from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from ai_core.pipelines.registry import list_pipelines, get_pipeline
from ai_core.pipelines.executor import run_pipeline
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["pipelines"])


@router.get("/pipelines")
def pipelines_list():
    pipelines = list_pipelines()
    return [
        {
            "pipeline": cfg.pipeline,
            "description": cfg.description,
            "tags": cfg.tags,
            "environment": cfg.environment,
            "entrypoint": cfg.entrypoint,
            "args": cfg.get_args(),
            "inputs": cfg.get_schema(),
            "cloud": cfg.cloud.model_dump() if cfg.cloud else None,
            "tracking": cfg.tracking.model_dump() if cfg.tracking else None,
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

    # Extract args from input data (allow flat or nested format)
    args_dict = raw_input_data.get("args", raw_input_data)
    logger.debug(f"Pipeline args: {args_dict}")

    # Run pipeline (validates args internally)
    try:
        logger.info(f"Starting pipeline '{pipeline_name}' execution...")
        results = run_pipeline(cfg, args_dict)
        logger.info(f"Pipeline '{pipeline_name}' completed with results: {results}")
    except ValidationError as error:
        raise HTTPException(status_code=422, detail=error.errors())
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    return {f"{pipeline_name}": "ok"}

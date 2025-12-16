from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from ai_core.pipelines.registry import list_pipelines, get_pipeline
from app.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["pipelines"])


@router.get("/pipelines")
def pipelines_list():
    pipelines = list_pipelines()
    return [
        {
            **pipeline.model_dump(exclude={"func", "inputs", "args"}),
            "args": pipeline.args.model_json_schema().get("properties"),
            "inputs": pipeline.inputs.model_json_schema().get("properties"),
        }
        for pipeline in pipelines
    ]

@router.get("/pipelines/{pipeline_name}")
def pipelines_get(pipeline_name: str):
    pipeline = get_pipeline(pipeline_name)
    return {
        **pipeline.model_dump(exclude={"func", "inputs", "args"}),
        "args": pipeline.args.model_json_schema(),
        "inputs": pipeline.inputs.model_json_schema().get("properties"),
    }


@router.post("/pipelines/{pipeline_name}/run")
def pipelines_run(pipeline_name: str, raw_input_data: dict):

    try:
        pipeline = get_pipeline(pipeline_name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Pipeline '{pipeline_name}' not found.")

    try:
        InputsSchema = pipeline.inputs
        logger.debug(f"Inputs schema: {InputsSchema.model_json_schema()}")
        logger.debug(f"Inputs data: {raw_input_data}")
        config = InputsSchema(**raw_input_data)  # validate inputs
        logger.debug(f"Inputs config: {config}")
        # Run pipeline
        logger.info(f"Starting pipeline {pipeline_name} execution...")
        results = pipeline.run(config)
        logger.info(f"Pipeline {pipeline.pipeline} completed with results: {results}")

        return {f"{pipeline_name}": "run"}

    except ValidationError as error:
        raise HTTPException(status_code=422, detail=error.errors())

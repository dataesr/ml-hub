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
            **pipeline.model_dump(exclude={"func", "schema", "args"}),
            "args": pipeline.args.model_json_schema().get("properties"),
            "schema": pipeline.schema.model_json_schema().get("properties"),
        }
        for pipeline in pipelines
    ]

@router.get("/pipelines/{pipeline_name}")
def pipelines_get(pipeline_name: str):
    pipeline = get_pipeline(pipeline_name)
    return {**pipeline.model_dump(exclude={"func", "schema", "args"}), "args": pipeline.args.model_json_schema()}


@router.post("/pipelines/{pipeline_name}/run")
def pipelines_run(pipeline_name: str, raw_input_data: dict):

    try:
        pipeline = get_pipeline(pipeline_name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Pipeline '{pipeline_name}' not found.")

    try:
        PipelineSchema = pipeline.schema
        pipeline_config = PipelineSchema(**raw_input_data)  # validate inputs

        # Run pipeline
        logger.info(f"Starting pipeline {pipeline_name} execution...")
        results = pipeline.run(pipeline_config)
        logger.info(f"Pipeline {pipeline.pipeline} completed with results: {results}")

        return {f"{pipeline_name}": "done"}

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

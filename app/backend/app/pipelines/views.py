from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from ai_core.pipelines.registry import list_pipelines_names, get_pipeline
from ai_core.utils.logger import get_logger


logger = get_logger(__name__)

router = APIRouter(tags=["pipelines"])

@router.get("/pipelines")
def pipelines_list_names():
    pipeline_names = list_pipelines_names()
    return {"pipelines": pipeline_names}


@router.get("/pipelines/{pipeline_name}")
def pipelines_get(pipeline_name: str):
    pipeline = get_pipeline(pipeline_name)
    return pipeline


@router.post("/pipelines/{pipeline_name}/run")
def pipelines_run(pipeline_name: str, raw_input_data: dict):

    try:
        pipeline = get_pipeline(pipeline_name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Pipeline '{pipeline_name}' not found.")

    try:
        PipelineClass = pipeline["class"]
        pipeline_config = PipelineClass(**raw_input_data)  # validate inputs
        pipeline_instance = PipelineClass(config=pipeline_config)

        # Run pipeline
        results = pipeline_instance.run()
        logger.info(f"Pipeline {pipeline.pipeline} completed with results: {results}")

        return {f"{pipeline_name}": "submitted"}

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from pipelines.registry import list_pipelines_names, get_pipeline, get_pipeline_schema

router = APIRouter(tags=["pipelines"])


@router.get("/pipelines")
def pipelines_list_names():
    pipeline_names = list_pipelines_names()
    return {"pipelines": pipeline_names}


@router.get("/pipelines/{pipeline_name}")
def pipelines_get(pipeline_name: str):
    pipeline = get_pipeline()
    return pipeline


@router.post("/jobs/{pipeline_name}/run")
def pipelines_run(pipeline_name: str, raw_input_data: dict):

    try:
        pipelineSchema = get_pipeline_schema(pipeline_name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Pipeline '{pipeline_name}' not found.")

    try:
        validated_config = pipelineSchema(**raw_input_data)
        # TODO: run logic

        return {f"{pipeline_name}": "submitted"}

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

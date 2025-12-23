from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from jsonref import replace_refs
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
            "args": (
                replace_refs(pipeline.args.model_json_schema(union_format="primitive_type_array"))
                if pipeline.args
                else None
            ),
            "inputs": (
                replace_refs(pipeline.inputs.model_json_schema(union_format="primitive_type_array"))
                if pipeline.inputs
                else None
            ),
        }
        for pipeline in pipelines
    ]


@router.get("/pipelines/{pipeline_name}")
def pipelines_get(pipeline_name: str):
    pipeline = get_pipeline(pipeline_name)
    return {
        **pipeline.model_dump(exclude={"func", "inputs", "args"}),
        "args": (
            replace_refs(pipeline.args.model_json_schema(union_format="primitive_type_array")) if pipeline.args else None
        ),
        "inputs": (
            replace_refs(pipeline.inputs.model_json_schema(union_format="primitive_type_array"))
            if pipeline.inputs
            else None
        ),
    }


@router.post("/pipelines/{pipeline_name}/run")
def pipelines_run(pipeline_name: str, raw_input_data: dict):

    try:
        pipeline = get_pipeline(pipeline_name)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Pipeline '{pipeline_name}' not found.")

    try:
        InputsSchema = pipeline.inputs
        if not InputsSchema:
            raise HTTPException(status_code=400, detail=f"Pipeline '{pipeline_name}' has no inputs.")
        logger.debug(f"Inputs schema: {InputsSchema.model_json_schema()}")

        # Get pipeline instance
        logger.debug(f"Validating input data: {raw_input_data}")
        config = InputsSchema.model_validate(raw_input_data)

        # Run pipeline
        logger.info(f"Starting pipeline '{pipeline_name}' execution...")
        results = pipeline.run(config)
        logger.info(f"Pipeline '{pipeline_name}' completed with results: {results}")

        return {f"{pipeline_name}": "ok"}

    except ValidationError as error:
        raise HTTPException(status_code=422, detail=error.errors())

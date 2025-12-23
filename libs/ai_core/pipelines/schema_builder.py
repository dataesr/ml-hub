# ai_core/pipelines/input_schema.py
from typing import Dict, Tuple, Any, Optional, Type
from pydantic import BaseModel, Field, create_model
from ai_core.tracking.schemas import TrackingConfig


def model_from_defaults(
    name: str,
    model: BaseModel,
) -> Type[BaseModel]:
    """
    Build a new BaseModel where:
    - fields with default values become Optional
    - defaults come from the provided instance
    """
    fields: Dict[str, Tuple[Any, Any]] = {}

    values = model.model_dump(exclude_unset=False)

    for field_name, field_info in model.__class__.model_fields.items():
        if values.get(field_name) is not None:
            # default exists → optional field
            fields[field_name] = (
                Optional[field_info.annotation],
                values[field_name],
            )
        else:
            # no default → keep original requirement
            fields[field_name] = (
                field_info.annotation,
                field_info,
            )

    return create_model(name, **fields)


def build_pipeline_input_model(
    *,
    args_model: Type[BaseModel],
    infrastructure_default: Optional[BaseModel] = None,
    tracking_default: Optional[TrackingConfig] = None,
) -> Type[BaseModel]:

    fields = {
        "args": (args_model, ...),
    }

    if infrastructure_default:
        infra_model = model_from_defaults(
            "PipelineInfrastructure",
            infrastructure_default,
        )
        fields["infrastructure"] = (infra_model, infrastructure_default)

    if tracking_default:
        track_model = model_from_defaults(
            "PipelineTracking",
            tracking_default,
        )
        fields["tracking"] = (track_model, tracking_default)

    return create_model("PipelineInputs", **fields)

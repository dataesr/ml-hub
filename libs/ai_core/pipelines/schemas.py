from pathlib import Path
import jsonref
from typing import Any, Dict, List, Literal, Optional, Tuple, Type
from pydantic import BaseModel, Field, create_model
from ai_core.tracking.schemas import TrackingConfig
from ai_core.cloud.schemas import CloudJobInfrastructure
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)

CONFIGS_DIR = Path(__file__).parent / "configs"

# Supported Python types in YAML arg definitions
_PYTHON_TYPE_MAP = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


class ArgField(BaseModel):
    """Schema for a single pipeline argument defined in YAML."""

    type: str = "str"
    default: Any = None
    required: bool = False
    description: str = ""


class PipelineConfig(BaseModel):
    """
    Full pipeline configuration loaded from a YAML file.

    This is the single source of truth for a pipeline: metadata, args with
    defaults, cloud infrastructure, and tracking config.
    """

    # Metadata
    pipeline: str
    description: str = ""
    tags: List[str] = Field(default_factory=list)

    # Execution
    entrypoint: Optional[str] = None  # "module.path:function" or None
    environment: Literal["cloud", "local"] = "cloud"

    # Pipeline arguments spec
    args: Dict[str, ArgField] = Field(default_factory=dict)

    # Infrastructure & tracking
    cloud: Optional[CloudJobInfrastructure] = None
    tracking: Optional[TrackingConfig] = None

    # Internal: base config name (for inheritance)
    base: Optional[str] = None

    def _build_args_model(self) -> Type[BaseModel]:
        """
        Dynamically build a Pydantic BaseModel from the args spec.

        Returns a model class where:
        - Fields with `required: true` are mandatory
        - Fields with a `default` value are optional
        """
        fields: Dict[str, Tuple[Any, Any]] = {}

        for name, field in self.args.items():
            python_type = _PYTHON_TYPE_MAP.get(field.type, str)

            if field.required:
                fields[name] = (python_type, Field(..., description=field.description))
            else:
                if field.default:
                    fields[name] = (python_type, Field(default=field.default, description=field.description))
                else:
                    fields[name] = (Optional[python_type], Field(default=None, description=field.description))

        model = create_model("Arguments", **fields)
        return model

    def _build_cloud_model(self) -> Type[BaseModel]:
        """
        Dynamically build a Pydantic BaseModel from the cloud spec.

        Returns a model class where:
        - Fields with `required: true` are mandatory
        - Fields with a `default` value are optional
        """
        fields: Dict[str, Tuple[Any, Any]] = {}

        values = self.cloud.model_dump(exclude_unset=False)

        for field_name, field_info in CloudJobInfrastructure.model_fields.items():
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

        return create_model("Cloud", __base__=CloudJobInfrastructure, **fields)

    def _build_tracking_model(self) -> Type[BaseModel]:
        """
        Dynamically build a Pydantic BaseModel from the tracking spec.

        Returns a model class where:
        - Fields with `required: true` are mandatory
        - Fields with a `default` value are optional
        """
        fields: Dict[str, Tuple[Any, Any]] = {}

        values = self.tracking.model_dump(exclude_unset=False)

        for field_name, field_info in TrackingConfig.model_fields.items():
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

        return create_model("Tracking", __base__=TrackingConfig, **fields)

    def _build_inputs_model(self) -> Type[BaseModel]:
        """
        Dynamically build a Pydantic BaseModel from the inputs spec.
        """
        fields: Dict[str, Tuple[Any, Any]] = {"args": (self._build_args_model(), Field(title="Pipeline arguments"))}
        if self.cloud:
            fields["cloud"] = (self._build_cloud_model(), Field(title="Cloud configuration", default=None))
        if self.tracking:
            fields["tracking"] = (self._build_tracking_model(), Field(title="Tracking configuration", default=None))
        return create_model("Inputs", **fields)

    def get_required_fields(self) -> List[str]:
        """Return names of args that must be provided by the user."""
        return [name for name, field in self.args.items() if field.required]

    def get_defaults(self) -> Dict[str, Any]:
        """Return a dict of arg_name → default_value for optional fields."""
        return {name: field.default for name, field in self.args.items() if not field.required}

    def get_args(self) -> Dict[str, Any]:
        """Return a dict of all args."""
        return self.args

    def get_schema(self) -> Dict[str, Any]:
        """Return the JSON Schema associated with the pipeline inputs."""
        schema = self._build_inputs_model().model_json_schema(union_format="primitive_type_array")
        return jsonref.replace_refs(schema)

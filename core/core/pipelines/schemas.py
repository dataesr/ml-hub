from pathlib import Path
import jsonref
from typing import Any, Dict, List, Literal, Optional, Tuple, Type, Union
from typing_extensions import TypeAliasType
from pydantic import BaseModel, Field, create_model, RootModel, PrivateAttr, model_validator
from core.tracking.schemas import TrackingConfig
from core.cloud.schemas import CloudJobInfrastructure
from core.utils.logger import get_logger

logger = get_logger(__name__)

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
    value: Union[int, float, str, bool, None] = None  # for runtime values

    def get_value(self) -> Any:
        if self.value is not None:
            return self.value
        if self.default is not None:
            return self.default
        if self.required:
            raise ValueError(f"Argument is required but no value or default provided: {self}")
        return None


Args = TypeAliasType("Args", "Union[Dict[str, Args], ArgField]")


class PipelineArgs(RootModel[Dict[str, Args]]):
    """Base model for pipeline arguments. Accept only ArgField or nested ArgFields."""

    def _resolve(self, args: Args, exclude_defaults: bool = False):
        if isinstance(args, ArgField):
            if exclude_defaults and args.value is None:
                return None
            return args.get_value()
        resolved = {}
        for key, value in args.items():
            resolved_value = self._resolve(value, exclude_defaults=exclude_defaults)
            if exclude_defaults:
                if resolved_value is not None:
                    resolved[key] = resolved_value
            else:
                resolved[key] = resolved_value
        return resolved

    def get_values(self, exclude_defaults: bool = False) -> Dict[str, Any]:
        """Flat dict of arg name -> resolved value, ready to pass to entrypoint."""
        return self._resolve(self.root, exclude_defaults=exclude_defaults)

    def to_values(self, exclude_defaults: bool = False) -> BaseModel:
        """Dynamically build a Pydantic model instance from the args values."""
        args_model = _build_args_model(self.root, model_name="args")
        return args_model.model_validate(self.get_values(exclude_defaults=exclude_defaults))

    pass


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
    args: PipelineArgs = None

    # Infrastructure & tracking
    cloud: Optional[CloudJobInfrastructure] = None
    tracking: Optional[TrackingConfig] = None

    # Internal: base config name (for inheritance)
    base: Optional[str] = None

    # Internal: dynamically built input model for args, cloud, and tracking sections
    _inputs_model: BaseModel = PrivateAttr(default=None)

    def model_post_init(self, __context: Any) -> None:
        args_model = _build_args_model(self.args.root, model_name="Arguments")
        fields: Dict[str, Tuple[Any, Any]] = {"args": (args_model, Field(title="Pipeline arguments"))}
        if self.cloud:
            cloud_model = _merge_model_from_defaults(CloudJobInfrastructure, self.cloud, model_name="Cloud")
            fields["cloud"] = (cloud_model, Field(title="Cloud configuration", default=None))
        if self.tracking:
            tracking_model = _merge_model_from_defaults(TrackingConfig, self.tracking, model_name="Tracking")
            fields["tracking"] = (tracking_model, Field(title="Tracking configuration", default=None))
        self._inputs_model = create_model("Inputs", **fields)

    @classmethod
    @model_validator(mode="before")
    def parse_args(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        raw_args = data.get("args", {})
        data["args"] = _parse_args(raw_args)
        return data

    def update_args(self, new_args: dict[str, Any]) -> "PipelineConfig":
        """Return a new instance with user run values merged in."""
        current_args = self.args.root
        updated_args = _update_args(current_args, new_args)
        self.args = PipelineArgs(root=updated_args)
        return self

    def get_schema(self) -> Dict[str, Any]:
        """Return the JSON Schema associated with the pipeline inputs."""
        schema = self._inputs_model.model_json_schema(union_format="primitive_type_array")
        return jsonref.replace_refs(schema)


def _build_args_model(spec: Dict[str, Args], model_name: str) -> Type[BaseModel]:
    """
    Recursively build a Pydantic BaseModel from a spec dict.
    A field is considered nested if it has no 'type' key (it's a group of sub-fields).
    """
    fields: Dict[str, Tuple[Any, Any]] = {}
    for name, field in spec.items():
        # --- Nested group: no 'type' key means it's a sub-model ---
        if isinstance(field, dict) and ("type" not in field or not isinstance(field["type"], str)):
            sub_model = _build_args_model(field, model_name=name.capitalize())
            fields[name] = (sub_model, Field(..., description=f"{name} configuration"))

        else:
            python_type = _PYTHON_TYPE_MAP.get(field.type, str)

            if field.required:
                fields[name] = (python_type, Field(..., description=field.description))
            elif field.default is not None:
                fields[name] = (python_type, Field(default=field.default, description=field.description))
            else:
                fields[name] = (Optional[python_type], Field(default=None, description=field.description))

    return create_model(model_name, **fields)


def _merge_model_from_defaults(
    base: Type[BaseModel], overrides: BaseModel, model_name: str | None = None
) -> Type[BaseModel]:
    """
    Build a new model from base with overriding values become defaults.
    Fields not overridden keep their original defaults / requiredness.
    """
    fields: Dict[str, Tuple[Any, Any]] = {}
    override_values = overrides.model_dump(exclude_unset=True)

    for field_name, field_info in base.model_fields.items():
        if field_name in override_values:
            # override value → set as default
            fields[field_name] = (Optional[field_info.annotation], override_values[field_name])
        else:
            # keep original field definition as-is
            fields[field_name] = (field_info.annotation, field_info)
    return create_model(model_name or base.__name__, __base__=base, **fields)


def _parse_args(raw_args: Dict[str, Any]) -> Dict[str, Args]:
    """
    Parse the `args:` section from YAML into ArgField objects.

    Supports two formats:
    - Full: `{ type: str, default: "train", description: "..." }`
    - Short: just a scalar value treated as the default
    """
    parsed = {}
    for name, spec in raw_args.items():
        if isinstance(spec, dict):
            if "type" not in spec or not isinstance(spec["type"], str):
                parsed[name] = _parse_args(spec)
            else:
                # If 'required' not explicitly set, infer from 'default' key presence
                if "required" not in spec and "default" not in spec:
                    spec["required"] = True
                parsed[name] = ArgField(**spec)
        else:
            # Short-form: bare value is the default
            inferred_type = type(spec).__name__ if spec is not None else "str"
            if inferred_type not in _PYTHON_TYPE_MAP:
                inferred_type = "str"
            parsed[name] = ArgField(type=inferred_type, value=spec, required=False)
    return parsed


def _update_args(current_args: Dict[str, Args], new_args: Dict[str, Any]) -> Dict[str, Args]:
    for key, val in new_args.items():
        if key not in current_args:
            raise KeyError(f"Unknown argument: {key}")

        current = current_args[key]

        if isinstance(current, ArgField):
            current.value = val
        else:
            _update_args(current, val)
    return current_args

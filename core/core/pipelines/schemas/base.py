"""
Base pipeline configuration class.

``PipelineConfig`` is the Pydantic base that every concrete pipeline config
class inherits from (see ``pipeline_configs.py``).  Subclasses declare their
own ``args`` field type annotation (e.g. ``Optional[FinetuneArgs]``) as well
as pipeline-specific defaults for ``pipeline``, ``entrypoint``, ``cloud``,
and ``tracking``.

Usage:
    class FinetuneCausalConfig(PipelineConfig):
        pipeline: str = "finetune-causal"
        args: Optional[FinetuneArgs] = None
        cloud: CloudJobInfrastructure = CloudJobInfrastructure(...)
        tracking: TrackingConfig = TrackingConfig(...)
"""

import jsonref
from typing import Any, Dict, List, Literal, Optional, Tuple, Type, Union, get_args, get_origin
from pydantic import BaseModel, Field, create_model
from core.tracking.schemas import TrackingConfig
from core.cloud.schemas import CloudJobInfrastructure
from core.configs.load import deep_merge
from core.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineConfig(BaseModel):
    """
    Base class for all pipeline configurations.

    Subclasses set class-level defaults for every field and narrow ``args``
    to a specific typed model (e.g. ``Optional[FinetuneArgs]``).

    Lifecycle:
      1. ``get_pipeline(name)`` returns a fresh instance — ``args`` is ``None``.
      2. ``update_args(dict)`` validates the user-supplied dict into the typed
         args instance and stores it on ``self.args``.
      3. ``exec_pipeline(config)`` uses ``config.args`` directly.
    """

    # Pipeline metadata
    pipeline: str = ""
    description: str = ""
    tags: List[str] = Field(default_factory=list)

    # Execution
    entrypoint: Optional[str] = None
    environment: Literal["cloud", "local"] = "cloud"

    # Typed args instance — None until update_args() is called
    args: Optional[BaseModel] = None

    # Infrastructure & tracking — concrete subclasses set their own defaults
    cloud: Optional[CloudJobInfrastructure] = None
    tracking: Optional[TrackingConfig] = None

    def _get_args_class(self) -> Optional[Type[BaseModel]]:
        """
        Resolve the concrete args class from this instance's ``args`` field
        annotation, unwrapping ``Optional[X]`` / ``Union[X, None]`` if needed.
        """
        if self.args is not None:
            return type(self.args)
        annotation = type(self).model_fields["args"].annotation
        if annotation is None:
            return None
        origin = get_origin(annotation)
        if origin is Union:
            for arg in get_args(annotation):
                if arg is not type(None) and isinstance(arg, type) and issubclass(arg, BaseModel):
                    return arg
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return annotation
        return None

    def update_args(self, new_args: Dict[str, Any]) -> "PipelineConfig":
        """
        Merge *new_args* into the current args and return self.

        When ``args`` is None (template), validates from scratch.
        When ``args`` is already set, deep-merges on top.
        """

        if not new_args:
            return self
        args_class = self._get_args_class()
        if args_class is None:
            logger.warning("update_args: pipeline '%s' has no args class — skipping", self.pipeline)
            return self
        base = self.args.model_dump() if self.args is not None else {}
        self.args = args_class.model_validate(deep_merge(base, new_args))
        return self

    def get_schema(self) -> Dict[str, Any]:
        """
        Return a JSON Schema object describing the user-facing inputs:
        ``args`` (required), ``cloud`` and ``tracking`` (optional overrides).
        """

        args_class = self._get_args_class()
        if args_class is None:
            return {}

        fields: Dict[str, Tuple[Any, Any]] = {
            "args": (args_class, Field(title="Pipeline arguments")),
        }
        if self.cloud is not None:
            cloud_model = _model_with_defaults(CloudJobInfrastructure, self.cloud, "Cloud")
            fields["cloud"] = (cloud_model, Field(title="Cloud configuration", default=None))
        if self.tracking is not None:
            tracking_model = _model_with_defaults(TrackingConfig, self.tracking, "Tracking")
            fields["tracking"] = (tracking_model, Field(title="Tracking configuration", default=None))

        inputs_model = create_model("Inputs", **fields)
        schema = inputs_model.model_json_schema(union_format="primitive_type_array")
        return jsonref.replace_refs(schema)


def _model_with_defaults(
    base_cls: Type[BaseModel],
    instance: BaseModel,
    model_name: str,
) -> Type[BaseModel]:
    """
    Build a variant of *base_cls* where every field that was set on *instance*
    becomes a default.  Unset fields keep their original definition.
    """

    fields: Dict[str, Tuple[Any, Any]] = {}
    set_values = instance.model_dump(exclude_unset=True)
    for name, field_info in base_cls.model_fields.items():
        if name in set_values:
            fields[name] = (Optional[field_info.annotation], set_values[name])
        else:
            fields[name] = (field_info.annotation, field_info)
    return create_model(model_name, __base__=base_cls, **fields)

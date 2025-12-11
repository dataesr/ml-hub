import pkgutil
import importlib
from typing import Dict, Any, List, Type, Callable
from pydantic import BaseModel, create_model, Field
from ai_core.schemas.jobs import JobInput
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)

# Stores pipelines job_class, input_schema, metadata
PIPELINE_REGISTRY: Dict[str, Dict[str, Any]] = {}


class PipelineRegistryBase(BaseModel):
    """Base schema for all pipeline registry arguments."""

    # Pipeline args
    pipeline: str
    args: Type[BaseModel]

    # Optional fields
    description: str = ""
    tags: List[str] = Field(default_factory=list)


class PipelineRegistryCloud(PipelineRegistryBase):
    """Schema for pipelines running on the remote cloud server."""

    infrastructure: JobInput
    environment: str = "cloud"


class PipelineRegistryLocal(PipelineRegistryBase):
    """Schema for local pipelines."""

    infrastructure: Type[BaseModel] | None = None
    environment: str = "local"


def _register_pipeline(register_args: PipelineRegistryCloud | PipelineRegistryLocal) -> Callable[[Type], Type]:
    """Register pipeline."""
    args = register_args.args
    infra = getattr(register_args, "infrastructure", None)

    # Build the composed schema bases, validating infra if provided
    bases: List[Type[BaseModel]] = [args]
    if infra:
        if isinstance(infra, type) and issubclass(infra, BaseModel):
            bases.append(infra)
        else:
            raise TypeError("Pipeline infrastructure must be a Pydantic BaseModel subclass.")
    schema = create_model(
        register_args.pipeline.title().replace("-", ""),
        __base__=tuple[type[BaseModel], ...](bases),
    )

    def decorator(cls):
        registry_data = register_args.model_dump(by_alias=True)
        registry_data["schema"] = schema
        registry_data["class"] = cls

        PIPELINE_REGISTRY[register_args.pipeline] = registry_data
        return cls

    return decorator


def register_pipeline_cloud(register_args: PipelineRegistryCloud) -> Callable[[Type], Type]:
    """Decorator for pipelines that run on remote cloud infrastructure."""
    return _register_pipeline(register_args)


def register_pipeline_local(register_args: PipelineRegistryLocal) -> Callable[[Type], Type]:
    """Decorator for pipelines that run locally."""
    return _register_pipeline(register_args)


def _scan_and_register_pipelines():
    """
    Scan folder 'pipelines' and populate pipelines register
    """
    try:
        pipeline_packages = importlib.import_module("ai_core.pipelines.pipelines")
    except Exception as error:
        raise ImportError(f"Error while scanning pipelines (details={error})")

    # Scan pipelines
    for _, module_name, _ in pkgutil.walk_packages(pipeline_packages.__path__, pipeline_packages.__name__ + "."):
        logger.debug(f"{module_name =}")
        try:
            # Trigger pipeline register decorator
            importlib.import_module(module_name)
        except Exception as error:
            logger.debug(f"Warning: Could not import module {module_name}: {error}")


def list_pipelines_names() -> List[str]:
    """List all registered pipelines names."""
    logger.debug("caca")
    if not PIPELINE_REGISTRY:
        _scan_and_register_pipelines()
    return list(PIPELINE_REGISTRY.keys())


def get_pipeline(name: str):
    """Get a registered pipeline."""
    if not PIPELINE_REGISTRY:
        _scan_and_register_pipelines()

    pipeline = PIPELINE_REGISTRY.get(name)
    if not pipeline:
        raise KeyError(f"Pipeline '{name}' not found in registry.")

    return pipeline


def get_pipeline_schema(name: str) -> Type[BaseModel]:
    """Get a registered pipeline schema."""
    pipeline = get_pipeline(name)
    return pipeline["schema"]

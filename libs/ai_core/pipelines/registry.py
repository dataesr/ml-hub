import pkgutil
import importlib
from typing import Dict, Literal, List, Type, Callable
from pydantic import BaseModel, Field, create_model
from ai_core.schemas.jobs import JobInput
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)

class PipelineRegistryBase(BaseModel):
    """Base schema for all pipeline registry arguments."""

    # Pipeline args
    pipeline: str
    args: Type[BaseModel]

    description: str = ""
    tags: List[str] = Field(default_factory=list)

    schema: Type[BaseModel] | None = None
    func: Callable | None = None
    environment: Literal["cloud", "local"]
    infrastructure: Type[BaseModel] | None = None

    def run(self, arguments: dict):
        if self.environment == "local":
            self.func(arguments)
        elif self.environment == "cloud":
            # TODO
            pass
        else:
            raise ValueError(f"Pipeline environment should be 'local' or 'cloud'.")


class PipelineRegistryCloud(PipelineRegistryBase):
    """Schema for pipelines running on remote cloud infrastructure."""
    environment: Literal["cloud"] = "cloud"
    infrastructure: JobInput


class PipelineRegistryLocal(PipelineRegistryBase):
    """Schema for local pipelines."""
    environment: Literal["local"] = "local"


# Stores pipelines job_class, input_schema, metadata
PIPELINE_REGISTRY: Dict[str, PipelineRegistryLocal | PipelineRegistryCloud] = {}


def _register_pipeline(pipeline: PipelineRegistryCloud | PipelineRegistryLocal) -> Callable[[Callable], Callable]:
    """Register pipeline."""
    name = pipeline.pipeline
    args = pipeline.args
    infra = getattr(pipeline, "infrastructure", None)

    # Build the composed schema bases, validating infra if provided
    bases: List[Type[BaseModel]] = [args]
    if infra:
        if isinstance(infra, type) and issubclass(infra, BaseModel):
            bases.append(infra)
        elif isinstance(infra, BaseModel):
            bases.append(infra.__class__)
        else:
            raise TypeError("Pipeline infrastructure must be a Pydantic BaseModel subclass or instance.")
    schema = create_model(
        name.title().replace("-", ""),
        __base__=tuple[type[BaseModel], ...](bases),
    )

    def decorator(func: Callable):
        pipeline.schema = schema
        pipeline.func = func
        PIPELINE_REGISTRY[name] = pipeline
        return func

    return decorator


def register_pipeline_cloud(pipeline: PipelineRegistryCloud) -> Callable[[Callable], Callable]:
    """Decorator for pipelines that run on remote cloud infrastructure."""
    return _register_pipeline(pipeline)


def register_pipeline_local(pipeline: PipelineRegistryLocal) -> Callable[[Callable], Callable]:
    """Decorator for pipelines that run locally."""
    return _register_pipeline(pipeline)


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


def list_pipelines() -> List[PipelineRegistryLocal | PipelineRegistryCloud]:
    """List all registered pipelines."""
    if not PIPELINE_REGISTRY:
        _scan_and_register_pipelines()
    return list[PipelineRegistryLocal | PipelineRegistryCloud](PIPELINE_REGISTRY.values())


def get_pipeline(name: str) -> PipelineRegistryLocal | PipelineRegistryCloud:
    """Get a registered pipeline."""
    if not PIPELINE_REGISTRY:
        _scan_and_register_pipelines()

    pipeline = PIPELINE_REGISTRY.get(name)
    if not pipeline:
        raise KeyError(f"Pipeline '{name}' not found in registry.")

    return pipeline

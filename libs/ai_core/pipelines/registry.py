import pkgutil
import importlib
from typing import Dict, Literal, List, Type, Callable, Optional
from pydantic import BaseModel, Field

from ai_core.cloud.schemas import CloudJobInfrastructure
from ai_core.pipelines.schema_builder import build_pipeline_schema
from ai_core.pipelines.execution import run_local, run_cloud
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)

PIPELINE_REGISTRY: Dict[str, "PipelineRegistryLocal | PipelineRegistryCloud"] = {}


class PipelineRegistryBase(BaseModel):
    pipeline: str
    args: Optional[Type[BaseModel]] = None
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    environment: Literal["cloud", "local"]
    infrastructure: Optional[BaseModel] = None
    func: Optional[Callable] = None
    schema: Optional[Type[BaseModel]] = None

    def run(self, config: BaseModel):
        if self.environment == "local":
            return run_local(self.func, config)
        elif self.environment == "cloud":
            return run_cloud(config, self.infrastructure)
        else:
            raise ValueError(f"Pipeline environment should be 'local' or 'cloud'.")


class PipelineRegistryCloud(PipelineRegistryBase):
    environment: Literal["cloud"] = "cloud"
    infrastructure: CloudJobInfrastructure


class PipelineRegistryLocal(PipelineRegistryBase):
    environment: Literal["local"] = "local"


def create_pipeline_decorator(pipeline: PipelineRegistryCloud | PipelineRegistryLocal) -> Callable[[Callable], Callable]:
    schema = build_pipeline_schema(pipeline.pipeline, pipeline.args, pipeline.infrastructure)
    
    def decorator(func: Callable) -> Callable:
        pipeline.schema = schema
        pipeline.func = func
        PIPELINE_REGISTRY[pipeline.pipeline] = pipeline
        logger.debug(f"Registered pipeline: {pipeline.pipeline} (environment={pipeline.environment})")
        return func
    
    return decorator


def register_pipeline_cloud(pipeline: PipelineRegistryCloud) -> Callable[[Callable], Callable]:
    return create_pipeline_decorator(pipeline)


def register_pipeline_local(pipeline: PipelineRegistryLocal) -> Callable[[Callable], Callable]:
    return create_pipeline_decorator(pipeline)


def load_pipeline_modules():
    try:
        pipeline_packages = importlib.import_module("ai_core.pipelines.pipelines")
    except Exception as error:
        raise ImportError(f"Error while scanning pipelines (details={error})")

    for _, module_name, _ in pkgutil.walk_packages(pipeline_packages.__path__, pipeline_packages.__name__ + "."):
        logger.debug(f"{module_name =}")
        try:
            importlib.import_module(module_name)
        except Exception as error:
            logger.debug(f"Warning: Could not import module {module_name}: {error}")


def ensure_pipelines_loaded():
    if not PIPELINE_REGISTRY:
        load_pipeline_modules()


def list_pipelines() -> List[PipelineRegistryLocal | PipelineRegistryCloud]:
    ensure_pipelines_loaded()
    return list(PIPELINE_REGISTRY.values())


def get_pipeline(name: str) -> PipelineRegistryLocal | PipelineRegistryCloud:
    ensure_pipelines_loaded()
    
    pipeline = PIPELINE_REGISTRY.get(name)
    if not pipeline:
        raise KeyError(f"Pipeline '{name}' not found in registry.")
    
    return pipeline

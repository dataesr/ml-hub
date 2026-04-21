"""
Pipeline executor — handles running pipelines locally or in the cloud.

Resolves the entrypoint function from the config, builds validated args,
and dispatches to the appropriate execution environment.
"""

import importlib
from typing import Any, Callable, Dict, Optional
from pydantic import BaseModel
from ai_core.cloud.build import build_command_args
from ai_core.cloud.compute import job_run
from ai_core.cloud.schemas import (
    CloudJobInfrastructure,
    CloudJobInputs,
    CloudJobVolume,
)
from ai_core.pipelines.schemas import PipelineConfig
from ai_core.tracking.schemas import TrackingConfig
from ai_core.utils.logger import get_logger
from ai_core.utils.secrets import SECRET_ENV_HF
from ai_core.utils.types import ENV

logger = get_logger(__name__)


def resolve_entrypoint(entrypoint: str) -> Callable:
    """
    Resolve a dotted entrypoint string to a callable.

    Format: "module.path:function_name"
    Example: "ai_core.pipelines.entrypoints.finetune_causal:run"
    """
    if ":" not in entrypoint:
        raise ValueError(f"Invalid entrypoint format '{entrypoint}'. " f"Expected 'module.path:function_name'")

    module_path, func_name = entrypoint.rsplit(":", 1)

    try:
        module = importlib.import_module(module_path)
    except ImportError as error:
        raise ImportError(f"Cannot import entrypoint module '{module_path}': {error}")

    func = getattr(module, func_name, None)
    if func is None:
        raise AttributeError(f"Function '{func_name}' not found in module '{module_path}'")

    if not callable(func):
        raise TypeError(f"Entrypoint '{entrypoint}' is not callable")

    return func


def _build_tracking_config(tracking: Optional[TrackingConfig]) -> Optional[TrackingConfig]:
    """Convert TrackingConfig from YAML config to TrackingConfig."""
    if not tracking:
        return None
    return TrackingConfig(**tracking.model_dump())


def _build_cloud_infrastructure(cloud: CloudJobInfrastructure) -> CloudJobInfrastructure:
    """Convert CloudJobInfrastructure from YAML to CloudJobInfrastructure."""
    volumes = [
        CloudJobVolume(
            container=v.container,
            mount=v.mount,
            region=v.region,
            permission=v.permission,
        )
        for v in cloud.volumes
    ]

    envs = [ENV(name=env.name, value=env.value) for env in cloud.envs]

    return CloudJobInfrastructure(
        image=cloud.image,
        name=cloud.name,
        command=cloud.command,
        gpu=cloud.gpu,
        cpu=cloud.cpu,
        flavor=cloud.flavor,
        envs=envs,
        volumes=volumes,
    )


def run_local(config: PipelineConfig, args: BaseModel, tracking: Optional[TrackingConfig] = None):
    """
    Run a pipeline locally by resolving and calling its entrypoint.
    """
    if not config.entrypoint:
        raise ValueError(f"Pipeline '{config.pipeline}' has no entrypoint defined.")

    func = resolve_entrypoint(config.entrypoint)

    logger.info(f"Running pipeline '{config.pipeline}' locally...")
    try:
        return func(args, tracking=tracking)
    except Exception as error:
        logger.error(f"Failed to run local pipeline '{config.pipeline}': {error}")
        raise


def run_cloud(config: PipelineConfig, args: BaseModel) -> dict:
    """
    Submit a pipeline as a cloud job on OVH AI.
    """
    if not config.cloud:
        raise ValueError(f"Pipeline '{config.pipeline}' has no cloud configuration.")

    infra = _build_cloud_infrastructure(config.cloud)
    tracking = _build_tracking_config(config.tracking)

    logger.info(f"Submitting cloud pipeline '{config.pipeline}'...")

    infra_dict = infra.model_dump(exclude_unset=True)
    logger.debug(f"Infrastructure: {infra_dict}")

    envs = list(infra_dict.get("envs", []))

    # Add HuggingFace secret as env
    envs.extend(SECRET_ENV_HF)

    # Add tracking envs
    if tracking:
        envs.extend(tracking.get_envs())

    # Build command arguments from pipeline args
    args_dict = args.model_dump(exclude_defaults=True)
    command_args = build_command_args({"pipeline": config.pipeline, **args_dict})

    inputs_dict = {
        **infra_dict,
        "envs": envs,
        "command_args": command_args,
    }

    job_config = CloudJobInputs.model_validate(inputs_dict)

    data = job_run(job_config)
    logger.info(f"Cloud pipeline '{config.pipeline}' submitted: {data.get('id')}")

    return data


def run_pipeline(config: PipelineConfig, args_dict: Dict[str, Any]) -> Any:
    """
    High-level pipeline execution: validate args and dispatch to local or cloud.
    """
    # Build and validate args
    ArgsModel = config._build_args_model()
    args = ArgsModel.model_validate(args_dict)

    if config.environment == "local":
        tracking = _build_tracking_config(config.tracking)
        return run_local(config, args, tracking=tracking)
    elif config.environment == "cloud":
        return run_cloud(config, args)
    else:
        raise ValueError(f"Unknown environment: {config.environment}")

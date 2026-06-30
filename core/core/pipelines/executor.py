"""
Pipeline executor — handles running pipelines locally or in the cloud.

Resolves the entrypoint function from the config, builds validated args,
and dispatches to the appropriate execution environment.
"""

import importlib
from typing import Any, Callable
from core.cloud.build import build_command_args
from core.cloud.compute import job_run
from core.cloud.schemas import (
    CloudJobInputs,
)
from core.pipelines.schemas import PipelineConfig
from core.utils.logger import get_logger
from core.utils.secrets import SECRET_ENV_HF

logger = get_logger(__name__)


def resolve_entrypoint(entrypoint: str) -> Callable:
    """
    Resolve a dotted entrypoint string to a callable.

    Format: "module.path:function_name"
    Example: "core.pipelines.entrypoints.finetune_causal:run"
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


def run_entrypoint(config: PipelineConfig):
    """
    Run a pipeline entrypoint.
    """
    if not config.entrypoint:
        raise ValueError(f"Pipeline '{config.pipeline}' has no entrypoint defined.")

    func = resolve_entrypoint(config.entrypoint)
    try:
        return func(config.args.to_values(), tracking=config.tracking)
    except Exception as error:
        logger.error(f"Failed to run pipeline '{config.pipeline}': {error}")
        raise


def submit_cloud(config: PipelineConfig) -> dict:
    """
    Submit a pipeline as a cloud job.
    """
    if not config.cloud:
        raise ValueError(f"Pipeline '{config.pipeline}' has no cloud configuration.")

    logger.info(f"Submitting cloud pipeline '{config.pipeline}'...")

    # Manage envs
    envs = config.cloud.envs
    # Add HuggingFace secret as env
    envs.extend(SECRET_ENV_HF)
    # Add tracking envs
    if config.tracking:
        envs.extend(config.tracking.get_envs())

    # Build command arguments from pipeline args
    args_dict = config.args.get_values(exclude_defaults=True)
    logger.debug(f"args_dict = {args_dict}")
    command_args = build_command_args({"pipeline": config.pipeline, **args_dict})

    inputs_dict = {
        **config.cloud.model_dump(exclude_defaults=True),
        "envs": envs,
        "command_args": command_args,
    }

    job_config = CloudJobInputs.model_validate(inputs_dict)

    data = job_run(job_config)
    logger.info(f"Cloud pipeline '{config.pipeline}' submitted: {data.get('id')}")

    return data


def exec_pipeline(config: PipelineConfig) -> Any:
    """Dispatches pipeline to local or cloud execution."""
    if config.environment == "local":
        return run_entrypoint(config)
    elif config.environment == "cloud":
        return submit_cloud(config)

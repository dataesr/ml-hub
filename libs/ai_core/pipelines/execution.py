from ai_core.utils.secrets import SECRET_ENV_HF
from ai_core.cloud.schemas import CloudJobInfrastructure
from typing import Callable, Optional
from pydantic import BaseModel
from ai_core.tracking.schemas import TrackingConfig
from ai_core.cloud.compute import job_run
from ai_core.utils.logger import get_logger
from ai_core.cloud.schemas import CloudJobInputs
from ai_core.cloud.build import build_command_args

logger = get_logger(__name__)


def run_local(pipeline: str, config: BaseModel, func: Optional[Callable]):
    """
    Run a pipeline locally.

    Expects config to have:
      - config.args
    """
    if not func:
        raise ValueError(f"Local pipeline {pipeline} has no function to execute.")
    return func(config)


def run_cloud(
    pipeline: str,
    config: BaseModel,
    infrastructure: Optional[CloudJobInfrastructure],
    tracking: Optional[TrackingConfig],
) -> dict:
    """
    Run a pipeline in the cloud.

    Expects config to have:
      - config.args
      - config.infrastructure
      - config.tracking
    """

    # Prefer config-provided infra/tracking, fallback to registry defaults
    infra = config.infrastructure or infrastructure
    track = config.tracking or tracking

    if not infra:
        raise ValueError(f"Cloud pipeline {pipeline} requires infrastructure configuration.")

    logger.info(f"Submitting cloud pipeline {pipeline}")

    infra_dict = infra.model_dump(exclude_unset=True)
    logger.debug(f"Infrastructure: {infra_dict}")

    envs = list(infra_dict.get("envs", []))

    # Add hugging face secret #TODO: move it elsewhere
    envs.extend(SECRET_ENV_HF)

    if track:
        envs.extend(track.get_envs())

    logger.debug(f"Envs: {envs}")

    inputs_dict = {
        **infra_dict,
        "envs": envs,
        "command_args": build_command_args({"pipeline": pipeline, **config.args.model_dump(exclude_defaults=True)}),
    }

    job_config = CloudJobInputs.model_validate(inputs_dict)

    data = job_run(job_config)
    logger.info(f'Cloud pipeline {pipeline} submitted: {data.get("id")}')

    return data

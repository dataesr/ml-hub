from ai_core.cloud.schemas import CloudJobInfrastructure
from typing import Callable, Optional
from pydantic import BaseModel
from ai_core.tracking.schemas import TrackingConfig
from ai_core.cloud.compute import job_run
from ai_core.utils.logger import get_logger
from ai_core.cloud.schemas import CloudJobInputs
from ai_core.cloud.build import build_command_args

logger = get_logger(__name__)


def run_local(config: BaseModel, func: Optional[Callable]):
    """
    Run a pipeline locally.

    Expects config to have:
      - config.args
    """
    if not func:
        raise ValueError("Local pipeline has no function to execute.")
    return func(config)


def run_cloud(
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
        raise ValueError("Cloud pipeline requires infrastructure configuration.")

    logger.info("Submitting cloud job")

    infra_dict = infra.model_dump(exclude_defaults=True)

    envs = list(infra_dict.get("envs", []))

    if track:
        envs.extend(track.get_envs())

    inputs_dict = {
        **infra_dict,
        "envs": envs,
        "command_args": build_command_args(config.args.model_dump(exclude_defaults=True)),
    }

    job_config = CloudJobInputs.model_validate(inputs_dict)

    data = job_run(job_config)
    logger.info(f'Cloud job submitted: {data.get("id")}')

    return data

from ai_core.cloud.schemas import CloudJobInfrastructure
from typing import Callable, Optional
from pydantic import BaseModel
from ai_core.tracking.schemas import TrackingConfig
from ai_core.cloud.compute import job_run
from ai_core.utils.logger import get_logger
from ai_core.cloud.schemas import CloudJobInputs
from ai_core.cloud.build import build_command_args

logger = get_logger(__name__)


def run_local(func: Callable, config: BaseModel):
    if not func:
        raise ValueError("Local pipeline has no function to execute.")
    return func(config)


def run_cloud(
    config: BaseModel, infrastructure: Optional[CloudJobInfrastructure] = None, tracking: Optional[TrackingConfig] = None
) -> dict:
    config_dict = config.model_dump(exclude_defaults=True)

    infra_dict = {}
    if infrastructure:
        infra_dict.update(**infrastructure.model_dump(exclude_defaults=True))
    infra_dict.update({k: config_dict.pop(k) for k in list(config_dict.keys()) if k in CloudJobInfrastructure.model_fields})

    track_dict = {}
    if tracking:
        track_dict.update(**tracking.model_dump(exclude_unset=True))
    track_dict.update({k: config_dict.pop(k) for k in list(config_dict.keys()) if k in TrackingConfig.model_fields})

    inputs_envs = infra_dict.get("envs", [])
    track_config = TrackingConfig(**track_dict)
    inputs_envs.extend(track_config.get_envs())

    inputs_dict = {
        **infra_dict,
        "envs": inputs_envs,
        "command_args": build_command_args(config_dict),
    }

    job_config = CloudJobInputs(**inputs_dict)
    data = job_run(job_config)  # start job
    logger.info(f'Cloud job submitted: {data.get("id")}')
    return data

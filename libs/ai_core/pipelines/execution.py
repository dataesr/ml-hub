from typing import Callable, Optional
from pydantic import BaseModel

from ai_core.cloud.compute import job_run
from ai_core.cloud.build import build_job
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


def run_local(func: Callable, config: BaseModel):
    if not func:
        raise ValueError("Local pipeline has no function to execute.")
    return func(config)


def run_cloud(config: BaseModel, infrastructure: Optional[BaseModel] = None) -> dict:
    if infrastructure:
        inputs_dict = infrastructure.model_dump(exclude_defaults=True)
        inputs_dict.update(**config.model_dump(exclude_unset=True))
    else:
        inputs_dict = config.model_dump(exclude_unset=True)
    
    job = build_job(inputs_dict)
    data = job_run(job)
    logger.info(f'Cloud job submitted: {data.get("id")}')
    return data

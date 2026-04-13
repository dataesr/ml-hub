from typing import no_type_check
from pydantic import BaseModel
from ai_core.pipelines.registry import register_pipeline_cloud, PipelineRegistryCloud
from ai_core.utils.logger import get_logger
from ai_core.cloud.schemas import CloudJobInfrastructure, CloudJobVolume
from ai_core.cloud.constants import CONFIGS_CONTAINER, DATASETS_CONTAINER, JOBS_CONTAINER

logger = get_logger(__name__)


class PipelineArgs(BaseModel):
    config_name: str


pipeline = PipelineRegistryCloud(
    pipeline="finetune-causal-axolotl",
    args=PipelineArgs,
    infrastructure=CloudJobInfrastructure(
        image="ghcr.io/dataesr/ml-hub/cuda-axolotl:latest",
        name="finetune-causal-axolotl",
        volumes=[
            CloudJobVolume(container=CONFIGS_CONTAINER, mount="configs"),
            CloudJobVolume(container=DATASETS_CONTAINER, mount="datasets"),
            CloudJobVolume(container=JOBS_CONTAINER, mount="jobs", permission="RWD"),
        ],
    ),
    description="Finetune a causal model with axolotl",
    tags=["finetuning", "causallm", "transformers", "axolotl"],
)


@no_type_check
@register_pipeline_cloud(pipeline)
def finetune_causal_axolotl(args: PipelineArgs):
    # no function, pipeline is directly executed by the image entrypoint
    # the entrypoint is defined in the Dockerfile
    return 0

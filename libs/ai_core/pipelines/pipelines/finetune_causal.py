from pydantic import BaseModel
from ai_core.pipelines.registry import register_pipeline_cloud, PipelineRegistryCloud
from ai_core.pipelines.interface import PipelineRunnerBase


class PipelineArgs(BaseModel):
    learning_rate: float = 2e-5
    epochs: int = 3


registry_args = PipelineRegistryCloud(
    pipeline="finetune-causal",
    args=PipelineArgs,
    infrastructure={"image": "ghcr.io/myorg/finetune-runner:latest"},
    description="Finetunes a CausalLM model on a custom dataset.",
    tags=[],
)


@register_pipeline_cloud(registry_args)
class PipelineRunner(PipelineRunnerBase):

    def run(self, config: BaseModel):
        print(f"Starting {config.pipeline} on image: {config.image}")
        print(f"Args: LR={config.learning_rate}, Epochs={config.epochs}")
        # ... execution logic ...

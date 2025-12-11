from pydantic import BaseModel
from libs.ai_core.registry import register_cloud_pipeline, PipelineRegistryCloud


class PipelineArgs(BaseModel):
    learning_rate: float = 2e-5
    epochs: int = 3


registry_args = PipelineRegistryCloud(
    pipeline="finetune-causal",
    args=PipelineArgs,
    infrastructure={"image": "ghcr.io/myorg/finetune-runner:latest"},
    description="Finetunes a CausalLM model on a custom dataset.",
    tags="",
)


@register_cloud_pipeline(registry_args)
class PipelineRunner:

    def run(self, config: BaseModel):
        print(f"Starting {config.pipeline} on image: {config.image}")
        print(f"Args: LR={config.learning_rate}, Epochs={config.epochs}")
        # ... execution logic ...

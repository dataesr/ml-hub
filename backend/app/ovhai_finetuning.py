import os
from pydantic import BaseModel
from typing import Literal
from app.logger import get_logger

logger = get_logger(__name__)

GPU = "ai1-1-gpu"
DOCKER = "ghcr.io/dataesr/llm-finetuning:latest"
DOCKER_CMD = "uv run main.py"
VOLUME_JOBS = "llm-jobs@1azgra/:/workspace/jobs:rwd"
VOLUME_DATASETS = "llm-datasets@1azgra/:/workspace/datasets:ro"
class ENV(BaseModel):
    name: str
    value: str

SECRET_ENVS: list[ENV] = [
    {"name": "HF_TOKEN", "value": os.getenv("HF_TOKEN")},
    {"name": "WANDB_KEY", "value": os.getenv("WANDB_KEY")},
]

class JOB(BaseModel):
    id: str | None = None
    name: str
    gpu: int | None = None
    model_name: str
    dataset_name: str
    dataset_format: Literal["auto", "conversational", "text"] | None = None
    dataset_volume: bool | None = False
    mode: Literal["train", "push"] | None = None
    push_model_dir: str | None = None
    hf_hub: str | None = None
    hf_hub_private: bool | None = False
    wandb_name: str | None = None
    wandb_project: str | None = None
    wandb_disabled: bool | None = False

    def _get_envs(self) -> list[ENV]:
        envs = SECRET_ENVS
        if self.wandb_name:
            envs.append({"name": "WANDB_NAME", "value": self.wandb_name})
        if self.wandb_project:
            envs.append({"name": "WANDB_PROJECT", "value": self.wandb_project})
        if self.wandb_disabled:
            envs.append({"name": "WANDB_MODE", "value": "disabled"})
        return envs

    def get_cli(self) -> str:
        cmd = f"--name {self.name}"
        if self.gpu:
            cmd += f" --flavor {GPU} --gpu {self.gpu}"
        else:
            cmd += f" --cpu 1"
        envs = self._get_envs()
        if envs:
            for env in envs:
                cmd += f" --env {env['name']}={env['value']}"
        cmd += f" --volume {VOLUME_JOBS}"
        if self.dataset_volume:
            cmd += f" --volume {VOLUME_DATASETS}"
        cmd += f" {DOCKER} -- {DOCKER_CMD}"
        cmd += f" --model_name {self.model_name}"
        cmd += f" --dataset_name {self.dataset_name}"
        if self.dataset_format:
            cmd += f" --dataset_format {self.dataset_format}"
        if self.mode:
            cmd += f" --mode {self.mode}"
        if self.push_model_dir:
            cmd += f" --push_model_dir {self.push_model_dir}"
        if self.hf_hub:
            cmd += f" --hf_hub {self.hf_hub}"
        if self.hf_hub_private:
            cmd += f" --hf_hub_private"
        return cmd

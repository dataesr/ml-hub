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


class JOB(BaseModel):
    id: str | None = None
    name: str
    gpu: int | None = None
    envs: list[ENV] = []
    model_name: str
    dataset_name: str
    dataset_format: Literal["auto", "conversational", "text"] | None = None
    dataset_volume: bool | None = False
    mode: Literal["train", "push"] | None = None
    output_model_name: str | None = None
    hf_hub: str | None = None
    hf_private: bool | None = False

    def get_cli(self) -> str:
        cmd = f"--name {self.name}"
        if self.gpu:
            cmd += f" --flavor {GPU} --gpu {self.gpu}"
        if self.envs:
            for env in self.envs:
                cmd += f" --env {env.name}={env.value}"
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
        if self.output_model_name:
            cmd += f" --output_model_name {self.output_model_name}"
        if self.hf_hub:
            cmd += f" --hf_hub {self.hf_hub}"
        if self.hf_private:
            cmd += f" --hf_private"
        return cmd

        # def _get_stop_cmd(self) -> str:
        #     if not self.id:
        #         raise ValueError(f"Job {self.name} doesnt have any id")
        #     cmd = f"ovhai job stop {self.id}"
        #     return cmd

        # def _get_data_cmd(self) -> str:
        #     if not self.id:
        #         raise ValueError(f"Job {self.name} doesnt have any id")
        #     cmd = f"ovhai job get {self.id} -o json"
        #     return cmd

import os
from app.ovhai import cmd_run
from app.types import ENV
from app.jobs.schemas import JOB_STATE, JOB_INPUTS
from app.datasets.service import create_config, add_config
from app.logger import get_logger

logger = get_logger(__name__)

GPU = "ai1-1-gpu"
DOCKER = "ghcr.io/dataesr/llm-finetuning:latest"
DOCKER_CMD = "uv run main.py"
VOLUME_JOBS = "llm-jobs@1azgra/:/workspace/jobs:rwd"
VOLUME_DATASETS = "llm-datasets@1azgra/:/workspace/datasets:ro"

SECRET_ENVS: list[ENV] = [
    {"name": "HF_TOKEN", "value": os.getenv("HF_TOKEN")},
    {"name": "WANDB_API_KEY", "value": os.getenv("WANDB_API_KEY")},
]


def _get_run_cmd(inputs: JOB_INPUTS):
    # Job command
    cmd = "ovhai job run -o json"
    cmd += f" --name {inputs.name}"

    # GPU
    if inputs.gpu:
        cmd += f" --flavor {GPU} --gpu {inputs.gpu}"
    else:
        cmd += f" --cpu 1"

    # ENVS
    envs = SECRET_ENVS
    if inputs.wandb_name:
        envs.append({"name": "WANDB_NAME", "value": inputs.wandb_name})
    if inputs.wandb_project:
        envs.append({"name": "WANDB_PROJECT", "value": inputs.wandb_project})
    if inputs.wandb_disabled:
        envs.append({"name": "WANDB_MODE", "value": "disabled"})
    for env in envs:
        cmd += f" --env {env['name']}={env['value']}"

    # Dataset extras
    dataset_extras = {}
    if inputs.dataset_instruction:
        dataset_extras["instruction"] = inputs.dataset_instruction
    if inputs.dataset_text_format:
        dataset_extras["text_format"] = inputs.dataset_text_format
    if inputs.dataset_chat_template:
        dataset_extras["chat_template"] = inputs.dataset_chat_template

    # Volumes
    cmd += f" --volume {VOLUME_JOBS}"
    if inputs.dataset_volume or dataset_extras:
        cmd += f" --volume {VOLUME_DATASETS}"

    # Docker args
    cmd += f" {DOCKER} -- {DOCKER_CMD}"
    cmd += f" --model_name {inputs.model_name}"
    cmd += f" --dataset_name {inputs.dataset_name}"
    if inputs.dataset_format:
        cmd += f" --dataset_format {inputs.dataset_format}"
    if dataset_extras:
        dataset_extras["dataset_name"] = inputs.dataset_name
        try:
            dataset_extras_name = add_config(create_config(dataset_extras))
            if dataset_extras_name:
                cmd += f" --dataset_extras_name {dataset_extras_name}"
        except Exception as error:
            logger.debug(f"dataset extras = {dataset_extras}")
            raise Exception(f"Error while adding dataset extras {str(error)}")
    if inputs.mode:
        cmd += f" --mode {inputs.mode}"
    if inputs.push_model_dir:
        cmd += f" --push_model_dir {inputs.push_model_dir}"
    if inputs.hf_hub:
        cmd += f" --hf_hub {inputs.hf_hub}"
    if inputs.hf_hub_private:
        cmd += f" --hf_hub_private"

    logger.debug(f"job cmd = {cmd}")
    return cmd


def get_all(state: JOB_STATE = None):
    filter = f"-s {state}" if state else "-a"
    cmd = f"ovhai job list -o json {filter}"
    data = cmd_run(cmd, capture_json=True)
    return data


def get(id: str):
    cmd = f"ovhai job get {id} -o json"
    data = cmd_run(cmd, capture_json=True)
    return data


def run(job_inputs: JOB_INPUTS):
    cmd = _get_run_cmd(job_inputs)
    data = cmd_run(cmd, capture_json=True)
    return data


def stop(id: str):
    cmd = f"ovhai job stop {id}"
    cmd_run(cmd)

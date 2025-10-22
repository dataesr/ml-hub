import os
import json
import subprocess
from app.logger import get_logger

logger = get_logger(__name__)

LLM_FINETUNING_GPU = "ai1-1-gpu"
LLM_FINETUNING_DOCKER = "ghcr.io/dataesr/llm-finetuning:latest"
LLM_FINETUNING_DOCKER_CMD = "uv run main.py"
LLM_FINETUNING_VOLUME = "llm-jobs@1azgra/:/workspace/jobs:rwd"


def ovhai_initialize():
    cmd = f'ovhai login --username {os.getenv("OVHAI_USERNAME")} --password-from-env OVHAI_PASSWORD'
    result = subprocess.run(cmd, shell=True, text=True)
    result.check_returncode()


def cmd_get_data(cmd: str):
    data = {}
    try:
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
        result.check_returncode()
        data = json.loads(result.stdout)
    except:
        logger.debug(f"error getting data for cmd {cmd}")
    return data


def ovhai_job_list():
    cmd = f"ovhai job list -o json"
    data = cmd_get_data(cmd)
    return data


def ovhai_job_run(args: dict):
    cmd = f"ovhai job run --name {args.name}"
    if args.gpu:
        cmd += f" --flavor {LLM_FINETUNING_GPU} --gpu 1"
    if args.envs:
        for env in args.env:
            cmd += f" --env {env.name}={env.value}"
    cmd += f" -- volume {LLM_FINETUNING_VOLUME}"
    cmd += f" {LLM_FINETUNING_DOCKER} -- {LLM_FINETUNING_DOCKER_CMD}"
    cmd += f" --model_name {args.model_name}"
    cmd += f" --dataset_name {args.dataset_name}"
    if args.dataset_format:
        cmd += f" --dataset_format {args.dataset_format}"
    if args.mode:
        cmd += f" --mode {args.mode}"
    if args.output_model_name:
        cmd += f" --output_model_name {args.output_model_name}"
    if args.hf_hub:
        cmd += f" --hf_hub {args.hf_hub}"
    if args.hf_private:
        cmd += f" --hf_private"

    data = cmd_get_data(cmd)
    return data


def ovhai_job_stop(id: str):
    cmd = f"ovhai job stop {id}"
    result = subprocess.run(cmd, shell=True, text=True)
    result.check_returncode()

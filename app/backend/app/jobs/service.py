import os
from app.types import ENV
from app.jobs.schemas import JOB_STATE, TRAIN_INPUTS, INFERE_INPUTS

# from app.datasets.service import create_config, add_config
from app.logger import get_logger
from ai_core.cloud.compute import job_list, job_get, job_stop, job_run

logger = get_logger(__name__)

GPU = "l4-1-gpu"
DOCKER_TRAIN = "ghcr.io/dataesr/llm-finetuning:latest"
DOCKER_INFERE = "ghcr.io/dataesr/llm-inference:latest"
DOCKER_CMD = "uv run main.py"
VOLUME_JOBS = "llm-jobs@1azgra/:/workspace/jobs:rwd"
VOLUME_COMPLETIONS = "llm-completions@1azgra/:/workspace/completions:rwd"
VOLUME_DATASETS = "llm-datasets@1azgra/:/workspace/datasets:ro"

SECRET_ENVS: list[ENV] = [
    {"name": "HF_TOKEN", "value": os.getenv("HF_TOKEN")},
    {"name": "MLFLOW_TRACKING_URI", "value": os.getenv("MLFLOW_TRACKING_URI")},
    {"name": "MLFLOW_TRACKING_USERNAME", "value": os.getenv("MLFLOW_TRACKING_USERNAME")},
    {"name": "MLFLOW_TRACKING_PASSWORD", "value": os.getenv("MLFLOW_TRACKING_PASSWORD")},
]


def _get_run_name(model_name: str, tag: str = None):
    name = model_name.split("/")[1].split("-")[0]
    if tag:
        name += f"-{tag}"
    return name.lower()


def _get_train_cmd(inputs: TRAIN_INPUTS):
    # Job command
    cmd = "ovhai job run -o json"
    cmd += f" --name train-{inputs.name or _get_run_name(inputs.model_name, inputs.pipeline)}"

    # GPU
    if inputs.gpu:
        cmd += f" --flavor {GPU} --gpu {inputs.gpu}"
    else:
        cmd += f" --cpu 1"

    # ENVS
    envs = SECRET_ENVS
    if inputs.envs:
        envs += inputs.envs
    if inputs.hf_push_repo:
        envs.append({"name": "HF_PUSH_REPO", "value": inputs.hf_push_repo})
    experiments_params = inputs.experiments_params
    if not experiments_params.disable:
        if experiments_params.name:
            envs.append({"name": "MLFLOW_RUN_NAME", "value": experiments_params.name})
        if experiments_params.name_tag:
            envs.append({"name": "MLFLOW_RUN_NAME_TAG", "value": experiments_params.name_tag})
        if experiments_params.project:
            envs.append({"name": "MLFLOW_EXPERIMENT_NAME", "value": experiments_params.project})
    if inputs.training_params:
        for key, value in inputs.training_params.items():
            envs.append({"name": key.upper(), "value": str(value)})
    for env in envs:
        cmd += f" --env {env['name']}={env['value']}"

    # Dataset extras
    dataset_extras = inputs.prompts_params

    # Volumes
    cmd += f" --volume {VOLUME_JOBS}"
    cmd += f" --volume {VOLUME_DATASETS}"

    # Docker args
    cmd += f" {DOCKER_TRAIN} -- {DOCKER_CMD}"
    cmd += f" --model_name {inputs.model_name}"
    cmd += f" --dataset_name {inputs.dataset_name}"
    if inputs.dataset_config:
        cmd += f" --dataset_config {inputs.dataset_config}"
    if not dataset_extras and inputs.dataset_format:
        cmd += f" --dataset_format {inputs.dataset_format}"
    if dataset_extras:
        dataset_extras["dataset_name"] = inputs.dataset_name
        if inputs.dataset_format:
            dataset_extras["dataset_format"] = inputs.dataset_format
        try:
            # dataset_config = add_config(create_config(dataset_extras))
            dataset_config = None
            if dataset_config:
                cmd += f" --dataset_config {dataset_config}"
        except Exception as error:
            logger.debug(f"dataset extras = {dataset_extras}")
            raise Exception(f"Error while adding dataset extras {str(error)}")
    if inputs.mode:
        cmd += f" --mode {inputs.mode}"
    if inputs.pipeline:
        cmd += f" --pipeline {inputs.pipeline}"
    if inputs.push_model_dir:
        cmd += f" --push_model_dir {inputs.push_model_dir}"

    logger.debug(f"train cmd = {cmd}")
    return cmd


def _get_infere_cmd(inputs: INFERE_INPUTS):
    # Job command
    cmd = "ovhai job run -o json"
    cmd += f" --name infere-{inputs.name or _get_run_name(inputs.model_name)}"

    # GPU
    if inputs.gpu:
        cmd += f" --flavor {GPU} --gpu {inputs.gpu}"
    else:
        cmd += f" --cpu 1"

    # ENVS
    envs = SECRET_ENVS
    if inputs.envs:
        envs += inputs.envs
    experiments_params = inputs.experiments_params
    if not experiments_params.disable:
        if experiments_params.name:
            envs.append({"name": "MLFLOW_RUN_NAME", "value": experiments_params.name})
        if experiments_params.name_tag:
            envs.append({"name": "MLFLOW_RUN_NAME_TAG", "value": experiments_params.name_tag})
        if experiments_params.project:
            envs.append({"name": "MLFLOW_EXPERIMENT_NAME", "value": experiments_params.project})
        if experiments_params.model_id:
            envs.append({"name": "MLFLOW_ACTIVE_MODEL_ID", "value": experiments_params.model_id})
    # if inputs.training_params:
    #     for key, value in inputs.training_params.items():
    #         envs.append({"name": key.upper(), "value": str(value)})
    for env in envs:
        cmd += f" --env {env['name']}={env['value']}"

    # Dataset extras
    dataset_extras = inputs.prompts_params

    # Volumes
    cmd += f" --volume {VOLUME_COMPLETIONS}"
    cmd += f" --volume {VOLUME_DATASETS}"

    # Docker args
    cmd += f" {DOCKER_INFERE} -- {DOCKER_CMD}"
    cmd += f" --model_name {inputs.model_name}"
    cmd += f" --dataset_name {inputs.dataset_name}"
    if inputs.dataset_config:
        cmd += f" --dataset_config {inputs.dataset_config}"
    if inputs.dataset_split:
        cmd += f" --dataset_split {inputs.dataset_split}"
    if dataset_extras:
        dataset_extras["dataset_name"] = inputs.dataset_name
        try:
            # dataset_config = add_config(create_config(dataset_extras))
            dataset_config = None
            if dataset_config:
                cmd += f" --dataset_config {dataset_config}"
        except Exception as error:
            logger.debug(f"dataset extras = {dataset_extras}")
            raise Exception(f"Error while adding dataset extras {str(error)}")

    logger.debug(f"infere cmd = {cmd}")
    return cmd


def _job_info(data: dict):
    infos = {
        "id": data["id"],
        "name": data["spec"]["name"],
        "task": data["spec"]["image"].split("/")[-1].split(":")[0].removeprefix("llm-"),
        "state": data["status"]["state"],
        "created_at": data.get("createdAt"),
        "updated_at": data.get("updatedAt"),
        "queued_at": data["status"].get("queuedAt"),
        "started_at": data["status"].get("startedAt"),
        "stopped_at": data["status"].get("stoppedAt"),
        "finalized_at": data["status"].get("finalizedAt"),
        "duration": data["status"].get("duration"),
        "url": data["status"].get("url"),
        "external_url": f'{os.getenv("OVHAI_URL", "")}/training/{data["id"]}',
        "image": data["spec"]["image"],
        "resources": data["spec"]["resources"],
        "labels": data["spec"]["labels"],
    }
    return infos


def get_all(state: JOB_STATE = None):
    data = job_list(state)
    jobs = [_job_info(job) for job in jobs]
    return jobs


def get(id: str):
    data = job_get(id)
    job = _job_info(data)
    return job


def run_train(job_inputs: TRAIN_INPUTS):
    data = job_run(_get_train_cmd(job_inputs))
    job = _job_info(data)
    return job


def run_infere(job_inputs: INFERE_INPUTS):
    data = job_run(_get_infere_cmd(job_inputs))
    return _job_info(data)


def stop(id: str):
    job_stop(id)

import requests
import time
import os
import pandas as pd
from datasets import Dataset
from retry import retry
from app.ovhai import cmd_run
from app.inference.schemas import (
    APP_STATE,
    APP_STATE_STOP,
    APP_STATE_START,
    APP_STATE_ERROR,
    COMPLETIONS_TASK_STATE,
    COMPLETIONS_PROMPTS_INPUTS,
)
from app.types import DICT_PARAMS
from app.logger import get_logger
from app.utils import env_exist, json_write, data_to_pandas
from app.ovhai import ovhai_object_upload

logger = get_logger(__name__)

CONTAINER_COMPLETIONS = "llm-completions"

### Inferences apps
def get_all(state: APP_STATE = None):
    filter = f"-s {state}" if state else ""
    cmd = f"ovhai app list -o json {filter}"
    data = cmd_run(cmd, capture_json=True)
    return data


def get(id: str):
    cmd = f"ovhai app get {id} -o json"
    data = cmd_run(cmd, capture_json=True)
    return data


def has_env(id: str, env_name: str, env_value: str):
    app = get(id)
    if env_exist(app["spec"]["envVars"], env_name=env_name, env_value=env_value):
        return True
    return False


def update_env(id: str, env_name: str, env_value: str):
    if not has_env(id, env_name=env_name, env_value=env_value):
        cmd = f"ovhai app update {id} --env {env_name}={env_value} -o json"
        updated_app = cmd_run(cmd, capture_json=True)

        # check modification is ok
        if not env_exist(updated_app["spec"]["envVars"], env_name=env_name, env_value=env_value):
            raise Exception(f"Error while updating app environment {env_name}")

    logger.info(f"Successfully updated app environment {env_name}")


def get_state(id: str):
    app = get(id)
    state = app["status"]["state"]
    return state


def get_url(id: str):
    app = get(id)
    url = app["status"]["url"]
    return url


def is_stopped(id: str):
    state = get_state(id)
    if state in APP_STATE_STOP:
        return True
    return False


def is_started(id: str):
    state = get_state(id)
    if state in APP_STATE_START:
        return True
    return False


def is_running(id: str):
    state = get_state(id)
    if state == "RUNNING":
        return True
    return False


def is_error(id: str):
    state = get_state(id)
    if state in APP_STATE_ERROR:
        return True
    return False


def start(id: str):
    cmd = f"ovhai app start {id}"
    cmd_run(cmd)


def stop(id: str):
    cmd = f"ovhai app stop {id}"
    cmd_run(cmd)


def start_model(id: str, model_name: str, wait_running: bool = False, wait_timeout: int = 60 * 15):
    if has_env(id, env_name="model_name", env_value=model_name):
        if is_started(id):
            logger.debug(f"App {id} already started...")
        else:
            start(id)
    else:
        if is_started(id):
            stop(id)
            time.sleep(5)
        update_env(id, env_name="model_name", env_value=model_name)
        start(id)

    if wait_running:
        start_time = time.time()
        while True:
            if is_running(id):
                return
            elif is_error(id):
                raise RuntimeError(f"App {id} starting failed")
            else:
                logger.debug(f"App {id} starting.....")
                time.sleep(30)

            current_time = time.time()
            if (current_time - start_time) > wait_timeout:
                raise RuntimeError(f"App {id} starting took too long ({current_time})")


### Completions tasks
def _completions_get_url(id: str = None, url: str = None):
    if not id and not url:
        raise ValueError(f"Please specify an inference url or app id!")
    if not url:
        try:
            url = get_url(id)
        except Exception as error:
            raise ValueError(f"Error while getting url from app {id}: {str(error)}")
    return f"{url}/generate"


@retry(delay=5, tries=3)
def _completions_safe_request(url, post_method: bool = False, post_json: dict = None, return_json: bool = True):
    if post_method:
        response = requests.post(url, json=post_json)
    else:
        response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error while getting completion task (details={response.text})")
    if return_json:
        data = response.json()
        return data
    return response


def completions_submit(
    prompts: list, id: str = None, url: str = None, prompts_params: dict = None, sampling_params: dict = None
) -> str:
    """Submit a completion task

    Args:
        prompts (list): list of prompts
        id (str): inference app id
        url (str): inference app url
        prompts_params (dict, optional): prompts additionnal params
        sampling_params (dict, optional): inference sampling params

    Returns:
        str: submitted task id
    """
    submit_url = _completions_get_url(id=id, url=url)

    body = {"prompts": prompts}
    if prompts_params:
        body["prompts_params"] = prompts_params
    if sampling_params:
        body["sampling_params"] = sampling_params

    data = _completions_safe_request(submit_url, post_method=True, post_json=body)
    task_id = data.get("task_id")
    task_status = data.get("status")
    logger.debug(f"Completions task {task_id} created (state={task_status})")
    return task_id


def completions_get_all(id: str = None, url: str = None):
    """Get all tasks from inference app

    Args:
        id (str): inference app id
        url (str): inference app url

    Returns:
        list: list of task_data
    """
    completions_url = _completions_get_url(id=id, url=url)
    tasks_url = f"{completions_url}/tasks"

    data = _completions_safe_request(url=tasks_url)
    return data


def completions_get(task_id: str, id: str = None, url: str = None, timeout: int = 60 * 15) -> tuple:
    """Get results of a completion task

    Args:
        task_id (str): task id
        id (str): inference app id
        url (str): inference app url
        timeout (int, optional): timeout for catching task results

    Returns:
        tuple[list, dict]: completions, task_data
    """
    completions_url = _completions_get_url(app_id=id, inference_url=url)
    task_url = f"{completions_url}/{task_id}"
    start_time = time.time()

    while True:
        data = _completions_safe_request(task_url)
        task_time = int(time.time() - start_time)

        task_status: COMPLETIONS_TASK_STATE | None = data.get("status")
        if task_status is None:
            logger.error(f"Generate task {task_id} not found!")
            raise KeyError(f"Generate task {task_id} not found")

        if task_status == "error":
            logger.error(f'Generate task {task_id} failed: {data.get("error")}')
            raise RuntimeError(f'Generate task {task_id} failed: {data.get("error")}')

        if task_status in ("queued", "running"):
            if timeout and (task_time > timeout):
                logger.warning(f"Generate task {task_id} took too long ({task_time}s), aborting...")
                raise RuntimeError(f"Generate task {task_id} took too long ({task_time}s)")
            logger.debug(f"Generate task {task_id} still {task_status}, retrying in 60s...")
            time.sleep(60)
            continue

        assert task_status == "done"
        completions = data.pop("completions")
        if not isinstance(completions, list):
            logger.error(f"Generate task {task_id} error: invalid completions format ({type(completions)})")
            raise ValueError(f"Generate task {task_id} error: invalid completions format ({type(completions)})")
        return completions, data


def _completions_get_prompts(inputs: COMPLETIONS_PROMPTS_INPUTS, inputs_col: str, to_list: bool = False):
    data = None

    # list str
    if isinstance(inputs, list) and all(isinstance(input, str) for input in inputs):
        data = pd.DataFrame({inputs_col: inputs})

    # dict
    if isinstance(inputs, list) and all(isinstance(input, dict) for input in inputs):
        data = pd.DataFrame.from_records(inputs)
        if not inputs_col in data.columns:
            raise ValueError(f"Prompts inputs: field '{inputs_col}' not found on dict")

    # pd.DataFrame
    if isinstance(inputs, pd.DataFrame):
        if not inputs_col in inputs.columns:
            raise ValueError(f"Prompts inputs: column '{inputs_col}' not found on DataFrame")
        data = inputs

    # Dataset
    if isinstance(inputs, Dataset):
        if not inputs_col in inputs.column_names:
            raise ValueError(f"Prompts inputs: column '{inputs_col}' not found on Dataset")
        data = inputs.to_pandas()

    if not data:
        raise ValueError(
            "Prompts inputs: Unsupported type. Must be list[str], list[dict], pandas DataFrame or HuggingFace Dataset."
        )

    if to_list:
        return data[inputs_col].astype(str).tolist()

    return data


def _completions_write(data: dict, write_path: str):
    file_path = json_write(path=write_path, data=data)
    ovhai_object_upload(file_path, CONTAINER_COMPLETIONS)
    os.remove(file_path)
    logger.debug(f"Completions saved at {write_path}")


def completions_pipeline(
    id: str,
    model_name: str,
    inputs: COMPLETIONS_PROMPTS_INPUTS,
    inputs_col: str = "input",
    outputs_col: str = "completion",
    prompts_params: DICT_PARAMS = None,
    sampling_params: DICT_PARAMS = None,
    return_only_completions: bool = True,
    write_results: bool = False,
) -> tuple:
    """Pipeline for generation of completions

    Args:
        id (str): inference app id
        model_name (str): model name
        inputs (promts_inputs): list or data with prompts
        inputs_col (str, optional): column name with prompts. Defaults to "input".
        outputs_col (str, optional): column name with completions. Defaults to "completion".
        prompts_params (dict, optional): prompts params (instruction, chat_template, text_format..)
        sampling_params (dict, optional): inference sampling params
        return_only_completions (bool, optional): return only completions. Defaults to True.
        write_results (bool, optional): write results on bucket. Defaults to False.

    Returns:
        tuple[list, dict]: completions, task_data
    """
    # Start inference app
    start_model(id=id, model_name=model_name, wait_running=True)

    # Format prompts
    data = _completions_get_prompts(inputs, inputs_col=inputs_col)
    prompts = data[inputs_col].astype(str).to_list()

    # Submit generation task
    task_id = completions_submit(prompts, id=id, prompts_params=prompts_params, sampling_params=sampling_params)
    logger.debug(f"Task id {task_id} submitted: {len(prompts)} texts")

    # Get generation task completions
    completions, task_data = completions_get(task_id, id=id)  # TODO: add timeout?
    logger.debug(f"Task id {task_id} results: {len(completions)} completions")

    if return_only_completions and not write_results:
        return completions, task_data

    # Check completions
    if not isinstance(completions, list):
        raise TypeError(f"Generated completions must be a list, got {type(completions)}")
    if len(completions) != len(prompts):
        logger.error(f"Generated {len(completions)} completions from {len(prompts)} texts")
        res = pd.DataFrame({outputs_col: completions})
        output: pd.DataFrame = pd.concat([data, res])
    else:
        logger.info(f"✅ Generated {len(completions)}")
        output = data
        output[outputs_col] = pd.Series(completions)

    # Write on disk if needed
    if write_results:
        _completions_write(output.to_dict(orient="records"), write_path=f"{model_name}/{task_id}")

    if return_only_completions:
        return completions, task_data

    return output, task_data

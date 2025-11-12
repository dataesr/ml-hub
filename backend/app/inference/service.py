import requests
import time
from retry import retry
from app.ovhai import cmd_run
from app.inference.schemas import APP_STATE, COMPLETIONS_TASK_STATE
from app.logger import get_logger
from app.utils import env_exist

logger = get_logger(__name__)


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


def update_env(id: str, env_name: str, env_value: str):
    data = get(id)
    if not env_exist(data["spec"]["envVars"], env_name=env_name, env_value=env_value):
        cmd = f"ovhai app update {id} --env {env_name}={env_value} -o json"
        updated_data = cmd_run(cmd, capture_json=True)

        # check modification is ok
        if not env_exist(updated_data["spec"]["envVars"], env_name=env_name, env_value=env_value):
            raise Exception(f"Error while updating app environment {env_name}")

    logger.info(f"Successfully updated app environment {env_name}")


def start(id: str):
    cmd = f"ovhai app start {id}"
    cmd_run(cmd)


def stop(id: str):
    cmd = f"ovhai app stop {id}"
    cmd_run(cmd)


### Generation tasks
def _get_inference_url(app_id: str = None, inference_url: str = None):
    if not app_id and not inference_url:
        raise ValueError(f"Please specify an inference url or app id!")
    if not inference_url:
        try:
            app = get(id)
            inference_url = app["status"]["url"]
        except Exception as error:
            raise ValueError(f"Error while getting url from app {app_id}: {str(error)}")
    return inference_url


def completions_pipeline(
    texts: list,
    id: str = None,
    url: str = None,
    prompts_params: dict = None,
    sampling_params: dict = None,
) -> tuple:
    """Pipeline for generation of completions

    Args:
        texts (list): list of texts
        inference_url (str): inference app url
        prompts_params (dict, optional): prompts params (instruction, chat_template, text_format..)
        sampling_params (dict, optional): inference sampling params

    Returns:
        tuple[list, dict]: completions, task_data
    """
    inference_url = _get_inference_url(app_id=id, inference_url=url)

    # Format prompts
    prompts = texts  # TODO

    # Submit generation task
    task_id = completions_submit(prompts, url=inference_url, prompts_params=prompts_params, sampling_params=sampling_params)
    logger.debug(f"for the {len(texts)} texts, task_id = {task_id}")

    # Get generation task completions
    completions, task_data = completions_get(task_id, url=inference_url)  # TODO: add timeout?
    logger.debug(f"got {len(completions)}")

    return completions, task_data


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
    submit_url = _get_inference_url(app_id=id, inference_url=url)

    body = {"prompts": prompts}
    if prompts_params:
        body["prompts_params"] = prompts_params
    if sampling_params:
        body["sampling_params"] = sampling_params

    response = requests.post(submit_url, json=body)
    response.raise_for_status()
    data = response.json()
    task_id = data.get("task_id")
    task_status = data.get("status")
    logger.debug(f"Generate task {task_id} created (state={task_status})")
    return task_id


@retry(delay=5, tries=3)
def completions_get_safe(url):
    response = requests.get(url)
    response.raise_for_status()
    return response


def completions_get_all(id: str = None, url: str = None):
    """Get all tasks from inference app

    Args:
        id (str): inference app id
        url (str): inference app url

    Returns:
        list: list of task_data
    """
    inference_url = _get_inference_url(app_id=id, inference_url=url)
    tasks_url = f"{inference_url}/tasks"

    response = requests.get(tasks_url)
    response.raise_for_status()
    data = response.json()
    return data


def completions_get(task_id: str, id: str = None, url: str = None, timeout: int = None) -> tuple:
    """Get results of a completion task

    Args:
        task_id (str): task id
        id (str): inference app id
        url (str): inference app url
        timeout (int, optional): timeout for catching task results

    Returns:
        tuple[list, dict]: completions, task_data
    """
    inference_url = _get_inference_url(app_id=id, inference_url=url)
    completions_url = f"{inference_url}/{task_id}"
    start_time = time.time()

    while True:
        response = completions_get_safe(completions_url)
        data = response.json()
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

import time
from ai_core.cloud.client import ovhai_run_cmd
from ai_core.utils.misc import env_exist
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)

# def _job_get_infos(data: dict):
#     infos = {
#         "id": data["id"],
#         "name": data["spec"]["name"],
#         "task": data["spec"]["image"].split("/")[-1].split(":")[0].removeprefix("llm-"),
#         "state": data["status"]["state"],
#         "created_at": data.get("createdAt"),
#         "updated_at": data.get("updatedAt"),
#         "queued_at": data["status"].get("queuedAt"),
#         "started_at": data["status"].get("startedAt"),
#         "stopped_at": data["status"].get("stoppedAt"),
#         "finalized_at": data["status"].get("finalizedAt"),
#         "duration": data["status"].get("duration"),
#         "url": data["status"].get("url"),
#         "external_url": f'{os.getenv("OVHAI_URL", "")}/training/{data["id"]}',
#         "image": data["spec"]["image"],
#         "resources": data["spec"]["resources"],
#         "labels": data["spec"]["labels"],
#     }
#     return infos


### --- compute jobs ---
def job_list(state: str = None):  # TODO: use schema
    filter = f"-s {state}" if state else "-a"
    cmd = f"ovhai job list -o json {filter}"
    data = ovhai_run_cmd(cmd, capture_json=True)
    return data


def job_get(id: str):
    cmd = f"ovhai job get {id} -o json"
    data = ovhai_run_cmd(cmd, capture_json=True)
    return data


def job_stop(id: str):
    cmd = f"ovhai job stop {id}"
    ovhai_run_cmd(cmd)


def job_start(cmd: str):
    data = ovhai_run_cmd(cmd, capture_json=True)
    return data


## --- compute apps ---
def app_list(state: str = None):  # TODO: use schema
    filter = f"-s {state}" if state else ""
    cmd = f"ovhai app list -o json {filter}"
    data = ovhai_run_cmd(cmd, capture_json=True)
    return data


def app_get(id: str):
    cmd = f"ovhai app get {id} -o json"
    data = ovhai_run_cmd(cmd, capture_json=True)
    return data


def app_has_env(id: str, env_name: str, env_value: str):
    app = app_get(id)
    if env_exist(app["spec"]["envVars"], env_name=env_name, env_value=env_value):
        return True
    return False


def app_update_env(id: str, env_name: str, env_value: str):
    if not app_has_env(id, env_name=env_name, env_value=env_value):
        cmd = f"ovhai app update {id} --env {env_name}={env_value} -o json"
        updated_app = ovhai_run_cmd(cmd, capture_json=True)

        # check modification is ok
        if not env_exist(updated_app["spec"]["envVars"], env_name=env_name, env_value=env_value):
            raise Exception(f"Error while updating app environment {env_name}")

    logger.info(f"Successfully updated app environment {env_name}")


def app_get_state(id: str):
    app = app_get(id)
    state = app["status"]["state"]
    return state


def app_get_url(id: str):
    app = app_get(id)
    url = app["status"]["url"]
    return url


def is_stopped(id: str):
    state = app_get_state(id)
    if state in ["STOPPING", "STOPPED", "FAILED", "ERROR"]:
        return True
    return False


def is_started(id: str):
    state = app_get_state(id)
    if state in ["QUEUED", "PENDING", "INITALIZING", "SCALING", "RUNNING"]:
        return True
    return False


def is_running(id: str):
    state = app_get_state(id)
    if state == "RUNNING":
        return True
    return False


def is_error(id: str):
    state = app_get_state(id)
    if state in ["FAILED", "ERROR"]:
        return True
    return False


def app_start(id: str):
    cmd = f"ovhai app start {id}"
    ovhai_run_cmd(cmd)


def app_stop(id: str):
    cmd = f"ovhai app stop {id}"
    ovhai_run_cmd(cmd)


def app_start_model(id: str, model_name: str, wait_running: bool = False, wait_timeout: int = 60 * 15):
    if app_has_env(id, env_name="model_name", env_value=model_name):
        if is_started(id):
            logger.debug(f"App {id} already started...")
        else:
            app_start(id)
    else:
        if is_started(id):
            app_stop(id)
            time.sleep(5)
        app_update_env(id, env_name="model_name", env_value=model_name)
        app_start(id)

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

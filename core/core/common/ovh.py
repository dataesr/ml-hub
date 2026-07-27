from core.utils.types import ENV
import os
import json
import shlex
from subprocess import CompletedProcess, run
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field
from core.utils.logger import get_logger

logger = get_logger(__name__)

# --- containers ---
CONTAINERS_REGION = "1azgra"
CONFIGS_CONTAINER = "llm-configs"
DATASETS_CONTAINER = "llm-datasets"
JOBS_CONTAINER = "llm-jobs"
COMPLETIONS_CONTAINER = "llm-completions"

# --- volumes ---
VOLUMES_PERMISSIONS = Literal["RO", "RW", "RWD"]  # read-only / read-write / read-write-delete
CONFIGS_VOLUME = "configs"
DATASETS_VOLUME = "datasets"
COMPLETIONS_VOLUME = "completions"
JOBS_VOLUME = "jobs"

# --- compute  ---
COMPUTE_GPU = "l4-1-gpu"
JOB_STATE = Literal[
    "QUEUED",
    "PENDING",
    "INITIALIZING",
    "FINALIZING",
    "RUNNING",
    "TIMEOUT",
    "FAILED",
    "ERROR",
    "DONE",
    "INTERRUPTED",
    "INTERRUPTING",
    "SYNC_FAILED",
]


def ovhai_initialize():
    # login
    cmd = [
        "ovhai",
        "login",
        "--username",
        os.getenv("OVHAI_USERNAME"),
        "--password-from-env",
        "OVHAI_PASSWORD",
    ]
    result: CompletedProcess = run(cmd, shell=False, text=True)
    result.check_returncode()

    # add s3 datastore
    cmd = [
        "ovhai",
        "datastore",
        "update",
        "s3",
        CONTAINERS_REGION,
        os.getenv("OVHAI_OS_ENDPOINT"),
        os.getenv("OVHAI_OS_REGION", "").lower(),
        os.getenv("OVHAI_OS_ACCESS_KEY"),
        "--secret-key-from-env",
        "OVHAI_OS_SECRET_KEY",
        "--store-credentials-locally",
    ]
    result: CompletedProcess = run(cmd, shell=False, text=True, capture_output=True)
    result.check_returncode()


def _run_cmd(cmd: list[str], capture_json: bool = False):
    result = run(cmd, shell=False, text=True, capture_output=True)
    if result.returncode != 0:
        message = result.stderr or result.stdout
        raise Exception(f"CMD ERR: {message}")

    if result.returncode == 0 and capture_json:
        try:
            data: dict = json.loads(result.stdout)
            return data
        except Exception:
            raise ValueError(f"Error while parsing json from {result.stdout}")


### --- ovhai objects ---
def ovhai_object_list(container: str, prefix: str | None = None):
    cmd = ["ovhai", "bucket", "object", "list", f"{container}@{CONTAINERS_REGION}", "-o", "json"]
    if prefix:
        cmd.extend(["--prefix", prefix])
    data = _run_cmd(cmd, capture_json=True)
    return data


def ovhai_object_upload(object_name: str, container: str, prefix: str | None = None, remove_prefix: str | None = None):
    cmd = ["ovhai", "bucket", "object", "upload", f"{container}@{CONTAINERS_REGION}", object_name]
    if prefix:
        cmd.extend(["--add-prefix", prefix])
    if remove_prefix:
        cmd.extend(["--remove-prefix", remove_prefix])
    _run_cmd(cmd)


def ovhai_object_download(
    object_name: str,
    container: str,
    output: str | None = None,
    remove_prefix: str | None = None,
) -> str:
    output_path = object_name
    cmd = ["ovhai", "bucket", "object", "download", f"{container}@{CONTAINERS_REGION}", object_name]
    if remove_prefix:
        cmd.extend(["--remove-prefix", remove_prefix])
        output_path = output_path.removeprefix(remove_prefix)
    if output:
        cmd.extend(["--output", output])
        output_path = os.path.join(output, output_path)
    _run_cmd(cmd)
    return output_path


def ovhai_object_delete(container: str, object_name: str | None = None, prefix: str | None = None):
    cmd = ["ovhai", "bucket", "object", "delete", f"{container}@{CONTAINERS_REGION}"]
    if object_name:
        cmd.append(object_name)
    elif prefix:
        cmd.extend(["--prefix", prefix])
    else:
        cmd.append("--all")
    _run_cmd(cmd)


### --- ovhai jobs ---
def job_list(state: JOB_STATE | None = None):  # TODO: use schema
    filter = ["-s", state] if state else ["-a"]
    cmd = ["ovhai", "job", "list", "-o", "json"]
    cmd.extend(filter)
    data = _run_cmd(cmd, capture_json=True)
    return data


def job_get(id: str):
    cmd = ["ovhai", "job", "get", id, "-o", "json"]
    data = _run_cmd(cmd, capture_json=True)
    return data


def job_stop(id: str):
    cmd = ["ovhai", "job", "stop", id]
    _run_cmd(cmd)


# def job_run(inputs: CloudJobInputs):
#     cli = build_cli_args(inputs)
#     logger.debug(f"Job CLI: {cli}")
#     data = _run_cmd(cli, capture_json=True)
#     return data
def job_run(cfg_args: list[str]):
    cmd = ["ovhai", "job", "run"]
    cmd.extend(["-o", "json"])  # output json
    cmd.extend(cfg_args)  # ovh job command
    logger.debug(f"Job command: {cmd}")
    data = _run_cmd(cmd, capture_json=True)
    return data


class OVHVolume(BaseModel):
    region: str = CONTAINERS_REGION
    container: str
    mount: str
    permission: VOLUMES_PERMISSIONS = "RO"

    def get_link(self):
        return f"{self.container}@{self.region}/:/workspace/{self.mount}:{self.permission}"


class OVHFlag(BaseModel):
    name: str
    value: Optional[str] = None

    def to_cmd(self) -> list[str]:
        cmd = [f'--{self.name.replace("_","-")}']
        if self.value:
            value_str = json.dumps(self.value) if isinstance(self.value, (list, dict)) else str(self.value)
            cmd.append(value_str)
        return cmd


class OVHConfig(BaseModel):
    # Image
    image: str
    command: list[str] = Field(default_factory=list)

    # Options
    name: Optional[str] = None
    cpu: Optional[int] = None
    gpu: Optional[int] = 1
    flavor: Optional[str] = COMPUTE_GPU
    envs: list[ENV] = Field(default_factory=list)
    volumes: list[OVHVolume] = Field(default_factory=list)
    labels: list[ENV] = Field(default_factory=list)

    def submit_job(self, flags: list[tuple[str, Any]], extra_envs: list[ENV] = []):
        """Converts the job object into a safe list of command line arguments."""
        args = []
        if self.name:
            args.extend(["--name", self.name])
        if self.gpu:
            args.extend(["--gpu", str(self.gpu)])
            if self.flavor:
                args.extend(["--flavor", self.flavor])
        if self.cpu:
            args.extend(["--cpu", str(self.cpu)])
        envs = list(self.envs)
        envs.extend(extra_envs)
        for env in envs:
            args.extend(["--env", f"{env.name}={env.value}"])
        for volume in self.volumes:
            args.extend(["--volume", shlex.quote(volume.get_link())])
        for label in self.labels:
            args.extend(["--label", f"{label.name}={label.value}"])
        args.append(self.image)
        args.append("--")
        args.extend(self.command)

        if flags:
            for key, value in flags:
                arg = [f'--{key.replace("_","-")}']
                if value is not None:
                    arg.append(str(value))
                args.extend(arg)

        return job_run(args)

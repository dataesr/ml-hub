import shlex
from pydantic import BaseModel, Field
from typing import List, Any
from ai_core.utils.types import ENV
from ai_core.cloud.schemas import CloudJobCommand, CloudJobInputs, CloudJobInfrastructure

# from ai_core.schemas.jobs import FinetuneInput, InfereInput


def build_cli_args(inputs: CloudJobInputs) -> list[str]:
    """Converts the job object into a safe list of command line arguments."""
    args = ["ovhai", "job", "run"]

    if inputs.name:
        args.extend(["--name", inputs.name])
    if inputs.gpu:
        args.extend(["--gpu", str(inputs.gpu)])
        if inputs.flavor:
            args.extend(["--flavor", inputs.flavor])
    if inputs.cpu:
        args.extend(["--cpu", str(inputs.cpu)])

    for env in inputs.envs:
        args.extend(["--env", f"{env.name}={shlex.quote(env.value)}"])

    for volume in inputs.volumes:
        args.extend(["--volume", shlex.quote(volume)])

    for label in inputs.labels:
        args.extend(["--label", f"{label.name}={shlex.quote(label.value)}"])

    args.append(inputs.image)

    if inputs.commands:
        args.append("--")
        for command in inputs.commands:
            arg = [f"--{command.name}"]
            if command.value:
                arg.append(f"{shlex.quote(command.value)}")
            args.extend(arg)

    return args


def build_cli_string(inputs: CloudJobInputs) -> str:
    """Converts the job object into a single shell command string."""
    args_list = build_cli_args(inputs)
    return shlex.join(args_list)


def build_command_args(config_dict: dict) -> List[CloudJobCommand]:
    """Convert a Pydantic model to a list of CommandArg objects.

    Args:
        config_dict: Pydantic model containing pipeline arguments

    Returns:
        List of CommandArg objects with name/value pairs
    """
    args_list = []
    for key, value in config_dict.items():
        arg_name = key.replace("_", "-")
        arg_value = str(value)
        args_list.append(CloudJobCommand(name=arg_name, value=arg_value))
    return args_list


def build_job(inputs: dict) -> CloudJobInputs:
    infra_dict = {k: v for k, v in inputs.items() if k in CloudJobInfrastructure.model_fields}
    args_dict  = {k: v for k, v in inputs.items() if k not in infra_dict.keys()}
    job_dict = {**infra_dict, "commands": build_command_args(args_dict)}
    job_inputs = CloudJobInputs(**job_dict)
    return job_inputs

import shlex
from typing import List
from ai_core.cloud.schemas import CloudJobArgument, CloudJobInputs
from ai_core.utils.misc import flatten_dict
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)

def build_cli_args(inputs: CloudJobInputs) -> list[str]:
    """Converts the job object into a safe list of command line arguments."""
    args = ["ovhai", "job", "run"]

    args.extend(["-o", "json"])  # output json

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
        args.extend(["--volume", shlex.quote(volume.get_link())])

    for label in inputs.labels:
        args.extend(["--label", f"{label.name}={shlex.quote(label.value)}"])

    args.append(inputs.image)

    args.append("--")

    args.extend(inputs.command)

    if inputs.command_args:
        for command in inputs.command_args:
            arg = [f"--{command.name}"]
            if command.value:
                arg.append(shlex.quote(command.value))
            args.extend(arg)

    return args


def build_cli_string(inputs: CloudJobInputs) -> str:
    """Converts the job object into a single shell command string."""
    args_list = build_cli_args(inputs)
    return shlex.join(args_list)


def build_command_args(config_dict: dict) -> List[CloudJobArgument]:
    """Convert a Pydantic model to a list of CommandArg objects.

    Args:
        config_dict: Pydantic model containing pipeline arguments

    Returns:
        List of CommandArg objects with name/value pairs
    """
    cmd_args: List[CloudJobArgument] = []
    flat_dict = flatten_dict(config_dict)
    for key, value in flat_dict.items():
        arg_name = str(key).replace("_", "-")  # convert to kebab-case for CLI
        arg_value = str(value)
        cmd_args.append(CloudJobArgument(name=arg_name, value=arg_value))
    return cmd_args

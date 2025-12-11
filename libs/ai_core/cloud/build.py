import shlex
from pydantic import BaseModel, Field
from typing import List, Any
from ai_core.schemas.types import ENV
from ai_core.schemas.jobs import FinetuneInput, InfereInput

class JobCommand(BaseModel):
    # Options
    name: str | None = None
    cpu: int | None = None
    gpu: int | None = None
    flavor: str | None = None
    envs: List[ENV] = Field(default_factory=list)
    volumes: List[str] = Field(default_factory=list)
    labels: List[ENV] = Field(default_factory=list)

    # Image
    image: str

    # Image command arguments
    commands: List[Any] = Field(default_factory=list)

    def to_cli_args(self) -> List[str]:
        """Converts the job object into a safe list of command line arguments."""
        args = ["ovhai", "job", "run"]

        if self.name:
            args.extend(["--name", self.name])
        if self.gpu:
            args.extend(["--gpu", str(self.gpu)])
            if self.flavor:
                args.extend(["--flavor", self.flavor])
        if self.cpu:
            args.extend(["--cpu", str(self.cpu)])

        for env in self.envs:
            args.extend(["--env", f"{env.name}={shlex.quote(env.value)}"])

        for volume in self.volumes:
            args.extend(["--volume", shlex.quote(volume)])

        for label in self.labels:
            args.extend(["--label", f"{label.name}={shlex.quote(label.value)}"])

        args.append(self.image)

        if self.commands:
            args.append("--")
            for command in self.commands:
                arg = [f"--{command.name}"]
                if command.value:
                    arg.append(f"{shlex.quote(command.value)}")
                args.extend(arg)

        return args

    def to_cli_string(self) -> str:
        """Converts the job object into a single shell command string."""
        args_list = self.to_cli_args()
        return shlex.join(args_list)


def build_finetune_command(job_input: FinetuneInput) -> JobCommand:
    job_command = JobCommand(
        name = f"ft-{job_input.model_name.split("/")[1].split("-")[0]}",
        image = "", #TODO: pipeline.get_image()
        **job_input
    )
    return job_command

def build_infere_command(job_input: InfereInput) -> JobCommand:
    job_command = JobCommand(
        name = f"inf-{job_input.model_name.split("/")[1].split("-")[0]}",
        image = "", #TODO: pipeline.get_image()
        **job_input
    )
    return job_command
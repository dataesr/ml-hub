from typing import Mapping
import json
from subprocess import CalledProcessError, Popen, PIPE, run
from core.utils.logger import get_logger

logger = get_logger(__name__)


def run_cmd(
    command: list[str],
    streaming: bool = False,
    capture_json: bool = False,
    check: bool = True,
    env: Mapping[str, str] | None = None,
    **kwargs,
):
    """Run a command in a subprocess, raising on non-zero return code when ``check`` is True."""

    try:
        if streaming:
            process = Popen(
                command,
                env=env,
                stdout=PIPE,
                stderr=PIPE,
                shell=False,
                text=True,
                bufsize=1,
                **kwargs,
            )

            stdout_lines = []
            stderr_lines = []

            if process.stdout is not None:
                for line in process.stdout:
                    cleaned = line.rstrip()
                    stdout_lines.append(cleaned)
                    logger.info(cleaned)

            if process.stderr is not None:
                for line in process.stderr:
                    cleaned = line.rstrip()
                    stderr_lines.append(cleaned)
                    logger.error(cleaned)

            returncode = process.wait()
            if check and returncode != 0:
                raise CalledProcessError(
                    returncode,
                    command,
                    output="\n".join(stdout_lines),
                    stderr="\n".join(stderr_lines),
                )

            return returncode

        # Not streaming, just run the command and capture output
        result = run(
            command,
            capture_output=True,
            shell=False,
            text=True,
            check=check,
            env=env,
            **kwargs,
        )

        if capture_json:
            try:
                data = json.loads(result.stdout)
                return data
            except Exception as error:
                raise ValueError(f"ERROR CMD: Error while parsing json from {result.stdout!r}") from error

        return result

    except CalledProcessError as error:
        err_msg = error.stderr or error.stdout
        logger.error(f"ERROR CMD {error.cmd}: {err_msg} (return code: {error.returncode})")
        raise

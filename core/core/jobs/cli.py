"""
Jobs runner — CLI entrypoint for running jobs.

Run a built-in job by name with optional arg overrides:
    iatelier run sft --model-name mistralai/Mistral-7B --epochs 5

Also accept yaml config:
    iatelier run sft --config path/to/my-config.yaml --epochs 5
"""

from core.utils.misc import deep_merge

import os
import typer
from pydantic import ValidationError
from core.common.configs import load_yaml_config
from core.jobs import JOBS_REGISTRY
from core.utils.logger import get_logger

logger = get_logger(__name__)

app = typer.Typer(name="iaterlier", help="Runner for AI jobs")


def _cast_value(value: str):
    """Cast a CLI string value to int, float, bool, or str."""
    for cast in (int, float):
        try:
            return cast(value)
        except (ValueError, TypeError):
            continue
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    return value


def _parse_override(unknown_args: list[str]) -> dict:
    """Parse unknown ``--key value`` CLI args into a nested dict."""

    iterator = iter(unknown_args)
    parsed = {}
    for key in iterator:
        if key.startswith("--"):
            key = key.lstrip("-").replace("-", "_")
            try:
                value = next(iterator)
                if value.startswith("--"):
                    parsed[key] = True
                    iterator = iter([value] + list(iterator))
                else:
                    parsed[key] = _cast_value(value)
            except StopIteration:
                parsed[key] = True

    # Expand dotted keys into nested dicts: "dataset.path" → {"dataset": {"path": ...}}
    overrides: dict = {}
    for key, value in parsed.items():
        parts = key.split(".")
        current = overrides
        for part in parts[:-1]:
            current.setdefault(part, {})
            current = current[part]
        current[parts[-1]] = value

    return overrides


# def _parse_cli_args() -> JOBS:
#     """Parse CLI arguments and return a job instance."""

#     parser = argparse.ArgumentParser(description="Runner for AI jobs")
#     exclusive = parser.add_mutually_exclusive_group(required=True)
#     exclusive.add_argument("--config", type=str, default=None, help="Path to a user YAML override file")
#     exclusive.add_argument("--job", type=str, default=None, help="Name of a built-in job")
#     args, unknown = parser.parse_known_args()

#     overrides = _parse_override(unknown)

#     if args.config:
#         if not os.path.exists(args.config):
#             print(f"Error: Config file not found: {args.config}", file=sys.stderr)
#             sys.exit(1)

#         user_cfg = load_yaml_config(args.config_path, from_disk=True)

#         return load_yaml_config(config_path, overrides=overrides)

#     if args.job:
#         try:
#             cfg = get_job(args.job).model_validate(overrides)
#         except KeyError as error:
#             print(f"Error: {error}", file=sys.stderr)
#             sys.exit(1)
#         return cfg

#     raise ValueError("Either --config or --job must be provided.")


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def run(
    ctx: typer.Context,
    job_name: str = typer.Argument(..., help=f"One of {list(JOBS_REGISTRY.keys())}"),
    config: str = typer.Option(None, "--config", help="Path to a job YAML config"),
    force_exec: bool = typer.Option(False, "--force_local", help="Force job execution locally"),
):
    """Pipeline runner CLI."""

    if job_name not in JOBS_REGISTRY:
        raise typer.BadParameter(f"Unknown job '{job_name}'. Available: {list(JOBS_REGISTRY.keys())}")

    job_cls = JOBS_REGISTRY[job_name]
    overrides = _parse_override(ctx.args)

    if config:
        if not os.path.exists(config):
            raise ValueError(f"Config path '{config}' not found.")
        job_cfg = load_yaml_config(config, from_disk=True)
        if overrides:
            job_cfg = deep_merge(job_cfg, {"args": overrides})
        job = job_cls.model_validate(job_cfg)
    else:
        job = job_cls.model_validate({"args": overrides})

    logger.info("--- Job %s ---", job.name)
    try:
        result = job.execute() if force_exec else job.submit(exec=True)
        logger.info("--- Success ---")
        return result
    except ValidationError as error:
        logger.error("Configuration validation failed: %s", error)
        raise
    except Exception as error:
        logger.error("Job %s failed: %s", job.name, error)
        raise


if __name__ == "__main__":
    app()

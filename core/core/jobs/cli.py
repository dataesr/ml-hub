"""
Jobs runner — CLI entrypoint for running jobs.

Run a built-in job by name with optional arg overrides:
    jobs run sft --model-name mistralai/Mistral-7B --epochs 5

Also accept yaml config:
    jobs run sft --config path/to/my-config.yaml --epochs 5
"""

import os
import argparse
from pydantic import ValidationError
from core.common.configs import load_yaml_config
from core.jobs import JOBS_REGISTRY
from core.utils.misc import deep_merge
from core.utils.logger import get_logger

logger = get_logger(__name__)

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


def run(job_name: str, config: str | None, force_exec: bool, extra_args: list[str]):
    if job_name not in JOBS_REGISTRY:
        raise ValueError(f"Unknown job '{job_name}'. Available: {list(JOBS_REGISTRY.keys())}")

    job_cls = JOBS_REGISTRY[job_name]
    overrides = _parse_override(extra_args)

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


def main():
    parser = argparse.ArgumentParser(description="CLI for AI jobs")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Run AI jobs")
    run_parser.add_argument("job_name", help=f"One of {list(JOBS_REGISTRY.keys())}")
    run_parser.add_argument("--config", default=None, help="Path to a job YAML config")
    run_parser.add_argument("--force-exec", action="store_true", default=False, help="Force job execution (no submit)")
    args, extra_args = parser.parse_known_args()

    if args.command == "run":
        run(args.job_name, args.config, args.force_exec, extra_args)


if __name__ == "__main__":
    main()

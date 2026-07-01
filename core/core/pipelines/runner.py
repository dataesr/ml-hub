"""
Pipeline runner — CLI entrypoint for running pipelines.

Supports two modes:
  1. Run a built-in pipeline by name with optional arg overrides:
       ai-pipeline-run --pipeline finetune-causal --model-name mistralai/Mistral-7B

  2. Run from a user YAML override file:
       ai-pipeline-run --config path/to/my-config.yaml --epochs 5
"""

import sys
import argparse
from pathlib import Path
from pydantic import ValidationError
from core.pipelines.schemas.base import PipelineConfig
from core.pipelines.registry import get_pipeline
from core.pipelines.load import load_user_config
from core.pipelines.executor import exec_pipeline, run_entrypoint
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


def _parse_cli_args() -> PipelineConfig:
    """Parse CLI arguments and return a fully configured PipelineConfig."""

    parser = argparse.ArgumentParser(description="Runner for AI pipelines")
    exclusive = parser.add_mutually_exclusive_group(required=True)
    exclusive.add_argument("--config", type=str, default=None, help="Path to a user YAML override file")
    exclusive.add_argument("--pipeline", "-p", type=str, default=None, help="Name of a built-in pipeline")
    args, unknown = parser.parse_known_args()

    overrides = _parse_override(unknown)

    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Config file not found: {config_path}", file=sys.stderr)
            sys.exit(1)
        return load_user_config(config_path, overrides=overrides)

    if args.pipeline:
        try:
            cfg = get_pipeline(args.pipeline)
        except KeyError as error:
            print(f"Error: {error}", file=sys.stderr)
            sys.exit(1)
        if overrides:
            cfg.update_args(overrides)
        return cfg

    raise ValueError("Either --config or --pipeline must be provided.")


def run_entrypoint_cli():
    """Pipeline entrypoint CLI."""

    config = _parse_cli_args()
    logger.info("--- Pipeline %s ---", config.pipeline)
    try:
        run_entrypoint(config)
        logger.info("--- Success ---")
    except ValidationError as error:
        logger.error("Configuration validation failed: %s", error)
        raise


def run_pipeline_cli():
    """Pipeline runner CLI."""

    config = _parse_cli_args()
    logger.info("--- Pipeline %s ---", config.pipeline)
    try:
        result = exec_pipeline(config)
        logger.info("--- Success ---")
        return result
    except ValidationError as error:
        logger.error("Configuration validation failed: %s", error)
        raise
    except Exception as error:
        logger.error("Pipeline %s failed: %s", config.pipeline, error)
        raise


if __name__ == "__main__":
    run_pipeline_cli()

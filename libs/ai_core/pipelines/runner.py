"""
Pipeline runner — CLI entrypoint for running pipelines.

Supports two modes:
  1. Run a built-in pipeline by name:
     ai-pipeline-run --pipeline finetune-causal -a model_name=mistralai/Mistral-7B-v0.3 -a dataset_name=my-data

  2. Run from a YAML config file:
     ai-pipeline-run --config path/to/my-config.yaml -a epochs=5
"""
from ai_core.pipelines.schemas import PipelineConfig
from typing import Any
import sys
import argparse
from pathlib import Path
from pydantic import ValidationError
from ai_core.pipelines.config import CONFIGS_DIR, load_user_config, load_pipeline_config
from ai_core.pipelines.executor import run_pipeline
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


def _cast_value(value: str) -> Any:
    """Cast values from CLI args to appropriate types (int, float, bool)."""
    # int, float handling
    for cast in (int, float):
        try:
            return cast(value)
        except (ValueError, TypeError):
            continue
    # boolean handling
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    return value


def parse_override(unknown_args: list[str]) -> dict:
    """Parse unknown CLI args into a nested dict."""
    iterator = iter(unknown_args)
    parsed = {}
    for key in iterator:
        if key.startswith("--"):
            key = key.lstrip("-").replace("-", "_")  # convert to snake case
            try:
                value = next(iterator)
                if value.startswith("--"):
                    # flag without value → treat as True
                    parsed[key] = True
                    # re-process this as next key
                    iterator = iter([value] + list(iterator))
                else:
                    parsed[key] = _cast_value(value)
            except StopIteration:
                parsed[key] = True

    overrides = {}
    for key, value in parsed.items():
        dotted_keys = key.split(".")
        current = overrides
        for k in dotted_keys[:-1]:
            current.setdefault(k, {})
            current = current[k]
        current[dotted_keys[-1]] = value

    return overrides


def parse_cli_args() -> PipelineConfig:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Runner for AI pipelines")
    exclusive = parser.add_mutually_exclusive_group(required=True)
    exclusive.add_argument("--config", type=str, default=None, help="Path to a user YAML config file")
    exclusive.add_argument("--pipeline", "-p", type=str, default=None, help="Name of a built-in pipeline")
    args, overrides = parser.parse_known_args()  # allow unknown args for overrides

    # Parse dotted.key=value arguments
    overrides = parse_override(overrides)

    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Config file not found: {config_path}", file=sys.stderr)
            sys.exit(1)
        config = load_user_config(config_path, overrides=overrides)
        return config

    if args.pipeline:
        config_path = CONFIGS_DIR / f"{args.pipeline}.yaml"
        if not config_path.exists():
            print(f"Error: Built-in pipeline '{args.pipeline}' not found.", file=sys.stderr)
            sys.exit(1)
        config = load_pipeline_config(config_path, overrides=overrides)
        return config

    # This should never happen due to mutually exclusive group
    raise ValueError("Either --config or --pipeline must be provided.")


def run_pipeline_cli():
    """Main CLI entrypoint."""
    config = parse_cli_args()
    logger.info(f"--- Start pipeline: {config.pipeline} ---")

    try:
        result = run_pipeline(config)
        logger.info(f"--- Pipeline {config.pipeline} completed ---")
        return result
    except ValidationError as error:
        logger.error(f"Configuration validation failed: {error}")
        raise
    except Exception as error:
        logger.error(f"Pipeline {config.pipeline} failed: {error}")
        raise


if __name__ == "__main__":
    run_pipeline_cli()

"""
Pipeline runner — CLI entrypoint for running pipelines.

Supports two modes:
  1. Run a built-in pipeline by name:
     ai-pipeline-run --pipeline finetune-causal -a model_name=mistralai/Mistral-7B-v0.3 -a dataset_name=my-data

  2. Run from a YAML config file:
     ai-pipeline-run --config path/to/my-config.yaml -a epochs=5
"""

import sys
import argparse
from pathlib import Path
from pydantic import ValidationError
from ai_core.pipelines.config import CONFIGS_DIR, load_user_config
from ai_core.pipelines.executor import run_pipeline
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


def _parse_override(arg_str: str) -> tuple:
    """Parse a key=value argument string."""
    if "=" not in arg_str:
        raise argparse.ArgumentTypeError(f"Argument must be in 'key=value' format, got: {arg_str}")
    key, value = arg_str.split("=", 1)

    # int, float handling
    for cast in (int, float):
        try:
            return key.strip(), cast(value)
        except (ValueError, TypeError):
            continue

    # boolean handling
    if value.lower() in ("true", "false"):
        return key.strip(), value.lower() == "true"

    return key.strip(), value


def _parse_cli_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Runner for AI pipelines")
    exclusive = parser.add_mutually_exclusive_group(required=True)
    exclusive.add_argument("--config", type=str, default=None, help="Path to a user YAML config file")
    exclusive.add_argument("--pipeline", "-p", type=str, default=None, help="Name of a built-in pipeline")
    parser.add_argument("-a", "--arg", action="append", default=[], help="Pipeline arguments (format: arg_name=value)")
    parsed_args = parser.parse_args()

    # Parse key=value arguments
    overrides = {}
    for arg_str in parsed_args.arg:
        key, value = _parse_override(arg_str)
        overrides[key] = value

    args_overrides = {"args": overrides} if overrides else {}

    if parsed_args.config:
        config_path = Path(parsed_args.config)
        if not config_path.exists():
            print(f"Error: Config file not found: {config_path}", file=sys.stderr)
            sys.exit(1)
        config = load_user_config(config_path, overrides=args_overrides)
        return config

    if parsed_args.pipeline:
        config_path = CONFIGS_DIR / f"{parsed_args.pipeline}.yaml"
        if not config_path.exists():
            print(f"Error: Built-in pipeline '{parsed_args.pipeline}' not found.", file=sys.stderr)
            sys.exit(1)
        config = load_user_config(config_path, overrides=args_overrides)
        return config


def run_pipeline_cli():
    """Main CLI entrypoint."""
    config = _parse_cli_args()

    # Get args dict from config defaults (CLI arguments have been merged as defaults)
    args_dict = config.get_defaults()

    logger.info(f"--- Start pipeline: {config.pipeline} ---")
    logger.debug(f"Args: {args_dict}")

    try:
        result = run_pipeline(config, args_dict)
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

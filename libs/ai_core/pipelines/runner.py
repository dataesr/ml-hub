import sys
import argparse
from pydantic import BaseModel, ValidationError
from ai_core.pipelines.registry import PIPELINE_REGISTRY, get_pipeline
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


def get_pipeline_args():
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument("--pipeline", type=str, required=True)
    known_args, _ = base_parser.parse_known_args()
    pipeline = get_pipeline(known_args.pipeline)

    full_parser = argparse.ArgumentParser(description=f"Runner for {pipeline.name}")
    full_parser.add_argument("--pipeline", type=str, required=True, help="Name of the pipeline to run.")
    for field_name, field_info in pipeline.args.model_fields.items():
        arg_name = f'--{field_name.replace("_","-")}'
        arg_type = str
        python_type = field_info.annotation
        if python_type in (int, float, bool):
            arg_type = python_type
        full_parser.add_argument(
            arg_name,
            type=arg_type,
            default=argparse.SUPPRESS,
            required=field_info.is_required(),
            help=field_info.description,
        )

    parsed_args = full_parser.parse_args(sys.argv[1:])
    config_dict = vars(parsed_args)

    try:
        args = pipeline.args(**config_dict)
    except ValidationError as error:
        logger.error(f"Configuration validation failed for pipeline {pipeline.name}")
        logger.error(f"CLI arguments received: {config_dict}")
        raise error

    return pipeline.name, pipeline.func, args


def run_pipeline():
    name, func, args = get_pipeline_args()
    logger.info(f"--- Start pipeline {name} ---")
    func(args)
    logger.info(f"--- Pipeline completed ---")
    return


if __name__ == "__main__":
    run_pipeline()

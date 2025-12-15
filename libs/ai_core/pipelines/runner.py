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

    pipeline_name = known_args.pipeline
    pipeline = get_pipeline(pipeline_name)

    func = pipeline["func"]
    PipelineArgs: BaseModel = pipeline["args"]

    full_parser = argparse.ArgumentParser(description=f"Runner for {pipeline_name}")
    full_parser.add_argument("--pipeline", type=str, required=True, help="Name of the pipeline to run.")
    for field_name, field_info in PipelineArgs.model_fields.items():
        arg_name = f'--{field_name.replace("_","-")}'
        python_type = field_info.annotation
        arg_type = str
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
        args = PipelineArgs(**config_dict)
    except ValidationError as error:
        logger.error(f"Configuration validation failed for pipeline {pipeline_name}")
        logger.error(f"CLI arguments received: {config_dict}")
        raise error

    return pipeline_name, func, args


def run_pipeline():
    name, func, args = get_pipeline_args()
    logger.info(f"--- Start pipeline {name} ---")
    func(args)
    logger.info(f"--- Pipeline completed ---")
    return


if __name__ == "__main__":
    run_pipeline()

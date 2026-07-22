"""
Run batch inference on a dataset using Scaleway.
"""
import asyncio

import mlflow
from pydantic import BaseModel, Field
from datasets import Dataset
from core.jobs.base import DatasetConfig
from core.common.scaleway import ChatCompletionParams, get_batch_completions, find_deployment
from core.common.mlflow import MLflowRun
from core.common.datasets import (
    load,
    get_prompts,
    should_use_chat_format,
    construct_one_prompt,
    construct_one_conversation,
    rename_columns,
    OUTPUT_COLUMN,
)
from core.utils.misc import timestamp
from core.utils.logger import get_logger

logger = get_logger(__name__)


class InferenceSCWArgs(BaseModel):
    """Arguments for the inference job (Scaleway inference)."""

    model_name: str = Field(..., description="Scaleway model name")
    dataset: DatasetConfig = Field(..., description="Dataset configuration")
    completion_params: ChatCompletionParams = Field(default=ChatCompletionParams())


def run_inference_scw(args: InferenceSCWArgs, mlf: MLflowRun):
    """Run batch inference on a dataset with Scaleway."""
    ### --- Get deployment ---
    deployment = find_deployment(model_name=args.model_name)
    deployment_url = deployment.get("url")
    if not deployment_url:
        raise ValueError(f"No deployment URL found for model name: {args.model_name}")

    ### --- Start tracking ---
    mlf.start_run(f"infer-{args.model_name}", tags={"run_type": "inference-scw"})
    mlf.set_active_model(model_name=args.model_name)

    ### --- Load dataset ---
    dataset = load(args.dataset.path, split=args.dataset.split)
    mlf.log_dataset(args.dataset.path, dataset, dataset_split=args.dataset.split)
    logger.info("✅ Dataset loaded")

    completion_params = args.completion_params
    if completion_params.model_dump(exclude_defaults=True):
        logger.debug(f"Custom sampling params: {completion_params.model_dump(exclude_defaults=True)}")
    mlf.log_params(completion_params.model_dump(exclude_unset=True))

    ### --- Get messages from dataset ---
    dataset = rename_columns(dataset, input_col=args.dataset.input_col)
    prompts = get_prompts(dataset)
    use_conversation = should_use_chat_format(args.dataset.format, args.dataset.chat_template)
    prompts = [
        (
            construct_one_conversation(prompt, system=args.dataset.system_prompt)
            if use_conversation
            else construct_one_prompt(prompt, instruction=args.dataset.system_prompt, text_format=args.dataset.text_format)
        )
        for prompt in prompts
    ]
    logger.info(f"✅ {len(prompts)} prompts formatted")
    logger.debug(f"Example: {prompts[0]}")

    ### --- Generate completions ---
    @mlflow.trace(name="scw_generate", span_type="llm")
    def scw_completions():
        completions = asyncio.run(get_batch_completions(prompts, args.model_name, deployment_url, args.completion_params))
        logger.debug(f"Generated {len(completions)} completions")
        return completions

    completions = scw_completions()

    ### --- Merge results ---
    output_col = args.dataset.output_col or OUTPUT_COLUMN
    if output_col in dataset.column_names:
        logger.warning(f"Existing column '{output_col}' will be overridden by generated completions!")

    # Check completions
    if not isinstance(completions, list):
        raise TypeError(f"Generated completions must be a list, got {type(completions)}")

    if len(completions) != len(dataset):
        logger.error(f"Generated {len(completions)} completions from {len(dataset)} texts, only completions will be saved")
        output = Dataset.from_dict({output_col: completions})
    else:
        logger.info(f"✅ Generated {len(completions)}")
        output: Dataset = dataset.add_column(output_col, completions)

    ### --- Write results ---
    file_name = f"completions_{timestamp()}.json"
    output_path = f"completions/{file_name}"
    output.to_json(output_path)
    mlf.log_artifact(output_path, file_name)

    ### --- Finalize ---
    logger.info(f"✅ Inference done! Results saved to {output_path}")

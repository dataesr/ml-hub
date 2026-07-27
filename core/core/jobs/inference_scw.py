"""
Run batch inference on a dataset using Scaleway.
"""

import asyncio
import mlflow
from pydantic import BaseModel, Field
from datasets import Dataset
from core.common.scaleway import ChatCompletionParams, get_batch_completions, find_deployment
from core.common.mlflow import MLflowRun
from core.common.datasets import (
    DatasetConfig,
    load_and_format_dataset,
    OUTPUT_COLUMN,
)
from core.utils.misc import timestamp
from core.utils.logger import get_logger

logger = get_logger(__name__)


class InferenceSCWArgs(BaseModel):
    """Arguments for the inference job (Scaleway inference)."""

    model_name: str = Field(..., description="Scaleway model name")
    dataset: DatasetConfig = Field(..., description="Dataset configuration")
    completion_params: ChatCompletionParams = Field(
        default=ChatCompletionParams(
            temperature=0,
            top_p=0.95,
            response_format={"type": "text"},
            stream=False,
            max_completion_tokens=4096,
        )
    )


def run_inference_scw(
    args: InferenceSCWArgs,
    mlf: MLflowRun,
    return_output_dataset: bool = False,
    start_tracking: bool = True,
):
    """Run batch inference on a dataset with Scaleway."""
    ### --- Get deployment ---
    deployment = find_deployment(model_name=args.model_name)
    deployment_url = deployment.get("url")
    if not deployment_url:
        raise ValueError(f"No deployment URL found for model name: {args.model_name}")

    ### --- Start tracking ---
    if start_tracking:
        mlf.start_run(f"infer-{args.model_name}", tags={"run_type": "inference-scw"})
    mlf.set_active_model(model_name=args.model_name)

    ### --- Load and format dataset ---
    dataset, _ = load_and_format_dataset(args.dataset)
    mlf.log_dataset(args.dataset.path, dataset, dataset_split=args.dataset.split)
    logger.info("✅ Dataset loaded")

    completion_params = args.completion_params
    if completion_params.model_dump(exclude_defaults=True):
        logger.debug(f"Custom sampling params: {completion_params.model_dump(exclude_defaults=True)}")
    mlf.log_params(completion_params.model_dump(exclude_unset=True))

    ### --- Prepare prompts ---
    prompts = dataset[dataset.column_names[0]]  # Use the first column as prompts
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
    if return_output_dataset:
        return output
    return output_path

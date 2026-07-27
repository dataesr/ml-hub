"""
Run inference and evaluation on the same dataset in one job.
"""

from pydantic import BaseModel, Field
from datasets import Dataset
from core.common.mlflow import MLflowRun
from core.jobs.evaluate import EvaluateInlineArgs, evaluate_dataframe
from core.jobs.inference_vllm import InferenceVLLMArgs, run_inference_vllm
from core.jobs.inference_scw import InferenceSCWArgs, run_inference_scw
from core.utils.logger import get_logger

logger = get_logger(__name__)


class InferAndEvalVLLMArgs(BaseModel):
    """Arguments for the infer+evaluate vLLM pipeline job."""

    inference: InferenceVLLMArgs = Field(..., description="Inference configuration")
    evaluation: EvaluateInlineArgs = Field(..., description="Evaluation configuration")


def run_infer_and_eval_vllm(args: InferAndEvalVLLMArgs, mlf: MLflowRun):
    """Run vLLM inference and then evaluate generated completions."""
    mlf.start_run(f"infer-eval-{args.inference.model_name}", tags={"run_type": "infer-and-eval-vllm"})
    output_dataset: Dataset = run_inference_vllm(
        args.inference,
        mlf,
        return_output_dataset=True,
        start_tracking=False,
    )
    logger.info("✅ Starting evaluation on generated completions")
    return evaluate_dataframe(output_dataset.to_pandas(), args.evaluation, mlf)  # ty:ignore[invalid-argument-type]


class InferAndEvalSCWArgs(BaseModel):
    """Arguments for the infer+evaluate Scaleway pipeline job."""

    inference: InferenceSCWArgs = Field(..., description="Inference configuration")
    evaluation: EvaluateInlineArgs = Field(..., description="Evaluation configuration")


def run_infer_and_eval_scw(args: InferAndEvalSCWArgs, mlf: MLflowRun):
    """Run Scaleway inference and then evaluate generated completions."""
    mlf.start_run(f"infer-eval-{args.inference.model_name}", tags={"run_type": "infer-and-eval-scw"})
    output_dataset: Dataset = run_inference_scw(
        args.inference,
        mlf,
        return_output_dataset=True,
        start_tracking=False,
    )
    logger.info("✅ Starting evaluation on generated completions")
    return evaluate_dataframe(output_dataset.to_pandas(), args.evaluation, mlf)  # ty:ignore[invalid-argument-type]

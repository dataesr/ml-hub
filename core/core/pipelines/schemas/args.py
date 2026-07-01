"""
Typed pipeline argument models.

Each pipeline has a concrete Pydantic class that declares its arguments with
types, defaults, and descriptions. These are used as the ``args`` field type
in the corresponding pipeline config class in ``pipeline_configs.py``.

Nested configs:
  DatasetConfig              -- common dataset fields
  FinetuneDatasetConfig      -- adds sensible text_format default
  UnslothDatasetConfig       -- adds instruction_part/response_part
  SamplingParamsConfig       -- vLLM sampling parameters

Args classes (one per pipeline):
  FinetuneArgs               -- finetune-causal
  FinetuneUnslothArgs        -- finetune-causal-unsloth
  InferenceArgs              -- dataset-inference
  EvaluateArgs               -- dataset-evaluate
  AxolotlArgs                -- finetune-causal-axolotl
"""

from typing import Optional
from pydantic import BaseModel, Field


class DatasetConfig(BaseModel):
    """Common dataset configuration shared across pipelines."""

    path: str = Field(..., description="HuggingFace dataset name or local path")
    split: str = Field("train", description="Dataset split to use")
    format: Optional[str] = Field(
        None,
        description="Dataset format ('chat' or 'text'). Inferred from structure when not set.",
    )
    text_format: Optional[str] = Field(
        None,
        description="Text prompt template in '{instruction}...{input}...{response}' form.",
    )
    system_prompt: Optional[str] = Field(None, description="System prompt prepended to all inputs")
    chat_template: Optional[str] = Field(None, description="Chat template for conversation formatting")
    instruction_col: str = Field("instruction", description="Column containing the instruction text")
    input_col: str = Field("input", description="Column containing the input text")
    output_col: str = Field("completion", description="Column containing the completion text")


class UnslothDatasetConfig(DatasetConfig):
    """Dataset config for the Unsloth pipeline (adds response-only training fields)."""

    instruction_part: Optional[str] = Field(
        None,
        description="Instruction part of the conversation (enables train-on-responses-only when set)",
    )
    response_part: Optional[str] = Field(
        None,
        description="Response part of the conversation (enables train-on-responses-only when set)",
    )


class SamplingParamsConfig(BaseModel):
    """vLLM sampling parameters."""

    seed: int = Field(0, description="Random seed")
    temperature: float = Field(0, description="Sampling temperature")
    max_tokens: int = Field(2048, description="Maximum tokens to generate")
    skip_special_tokens: bool = Field(False, description="Skip special tokens in output")


class FinetuneArgs(BaseModel):
    """Arguments for the finetune-causal pipeline (LoRA + BitsAndBytes 4-bit)."""

    model_name: str = Field(..., description="HuggingFace model name or path")
    dataset: DatasetConfig = Field(..., description="Dataset configuration")

    hf_push_repo: Optional[str] = Field(
        None,
        description="HuggingFace repo ID to push the finetuned model to. Skipped when not set.",
    )

    # LoRA parameters
    lora_r: int = Field(16, description="LoRA rank")
    lora_alpha: int = Field(32, description="LoRA alpha")
    lora_dropout: float = Field(0.05, description="LoRA dropout rate")

    # Training parameters
    max_seq_length: int = Field(8192, description="Maximum sequence length")
    epochs: int = Field(3, description="Number of training epochs")
    max_steps: int = Field(-1, description="Max training steps (-1 for unlimited)")
    batch_size: int = Field(1, description="Per-device train batch size")
    grad_acc_steps: int = Field(4, description="Gradient accumulation steps")
    optim: str = Field("paged_adamw_8bit", description="Optimizer name")
    learning_rate: float = Field(2e-5, description="Learning rate")
    lr_scheduler_type: str = Field("linear", description="Learning rate scheduler type")
    weight_decay: float = Field(0.001, description="Weight decay")
    max_grad_norm: float = Field(0.3, description="Maximum gradient norm for clipping")
    warmup_ratio: float = Field(0.03, description="Warmup ratio")
    warmup_steps: int = Field(0, description="Warmup steps (overrides warmup_ratio)")
    save_steps: int = Field(500, description="Save checkpoint every N steps")
    logging_steps: int = Field(50, description="Log metrics every N steps")


class FinetuneUnslothArgs(FinetuneArgs):
    """Arguments for the finetune-causal-unsloth pipeline."""

    dataset: UnslothDatasetConfig = Field(..., description="Dataset configuration")


class InferenceArgs(BaseModel):
    """Arguments for the dataset-inference pipeline (vLLM batch inference)."""

    model_name: str = Field(..., description="HuggingFace model name or path")
    dataset: DatasetConfig = Field(..., description="Dataset configuration")
    max_model_len: int = Field(2048, description="vLLM max model length")
    sampling_params: SamplingParamsConfig = Field(
        default_factory=SamplingParamsConfig,
        description="vLLM sampling parameters",
    )


class EvaluateArgs(BaseModel):
    """Arguments for the dataset-evaluate pipeline (MLflow scorers)."""

    dataset_name: str = Field(..., description="Name of the completions file to evaluate")
    model_name: str = Field("unnamed", description="Model name for tracking purposes")
    container: str = Field("llm-completions", description="OVH storage container name")
    scorers: Optional[str] = Field(None, description="Comma-separated list of scorer names to use")
    input_col: str = Field("inputs", description="Column containing the input text")
    output_col: str = Field("outputs", description="Column containing the model completions")
    expectation_col: str = Field("expectations", description="Column containing the expected outputs")
    id_col: str = Field("id", description="Column containing the row identifier")


class AxolotlArgs(BaseModel):
    """Arguments for the finetune-causal-axolotl pipeline."""

    config_name: str = Field(..., description="Name of the Axolotl config file (in configs/ volume)")

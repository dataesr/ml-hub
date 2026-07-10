"""
Finetune a causal LM with LoRA + BitsAndBytes (4-bit quantization).
"""

import os
from typing import no_type_check, Optional, Any
from pydantic import BaseModel, Field
from core.jobs.base import DatasetConfig
from core.common.mlflow import MLflowRun
from core.common.datasets import load, construct_prompts, rename_columns, should_use_chat_format
from core.common.models import push_model_to_hf, merge_adapters_to_model
from core.utils.files import folder_create
from core.utils.logger import get_logger

logger = get_logger(__name__)


class SFTArgs(BaseModel):
    """Arguments for the finetune-causal job (LoRA + BitsAndBytes 4-bit)."""

    model_name: str = Field(..., description="HuggingFace model name or path")
    dataset: DatasetConfig = Field(..., description="Dataset configuration")
    hf_push_repo: Optional[str] = Field(None, description="HuggingFace repo ID to push the model to.")

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


@no_type_check
def run_sft(args: SFTArgs, mlf: MLflowRun):
    """Finetune a causal LM with LoRA + BitsAndBytes."""
    # GPU imports inside the function to avoid dependencies at import time
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig, TaskType, prepare_model_for_kbit_training
    from trl import SFTConfig, SFTTrainer

    ### --- Start tracking ---
    mlf.start_run(f"sft-{args.model_name}", tags={"run_type": "sft-training"})

    ### --- Setup ---
    model_dir: str = folder_create(os.path.join("jobs", args.model_name))
    output_dir = os.path.join(model_dir, "output")
    checkpoint_dir = os.path.join(output_dir, "checkpoints")
    finetuned_dir = os.path.join(output_dir, "finetuned")

    ### --- Load model and tokenizer ---
    logger.info(f"Start loading model {args.model_name}")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    tokenizer.padding_side = "right"  # to prevent warnings
    max_seq_length = args.max_seq_length
    if hasattr(tokenizer, "max_length") and tokenizer.max_length < max_seq_length:
        logger.warning(f"Overrriding tokenizer max_length from {tokenizer.max_length} to {max_seq_length}")
        tokenizer.max_length = max_seq_length

    # Load model in 4bit
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=False,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    model = AutoModelForCausalLM.from_pretrained(args.model_name, device_map="auto", quantization_config=bnb_config)
    model.config.use_cache = False
    model.config.pretraining_tp = 1
    model.config.pad_token_id = tokenizer.pad_token_id

    # Prepare model for lora
    model = prepare_model_for_kbit_training(
        model, use_gradient_checkpointing=True, gradient_checkpointing_kwargs={"use_reentrant": False}
    )

    logger.debug(f"Model embeddings size: {model.get_input_embeddings().weight.size(0)}")
    logger.debug(f"Tokenizer template: {tokenizer.chat_template}")
    logger.info("✅ Model and tokenizer loaded")

    ### --- Load dataset ---
    dataset = load(args.dataset.path, split=args.dataset.split)
    mlf.log_dataset(args.dataset.path, dataset, dataset_split=args.dataset.split)
    logger.info("✅ Dataset loaded")

    ### --- Format prompts ---
    dataset = rename_columns(dataset, args.dataset.instruction_col, args.dataset.input_col, args.dataset.output_col)
    dataset = construct_prompts(
        dataset,
        custom_instruction=args.dataset.system_prompt,
        custom_text_format=args.dataset.text_format,
        use_conversational_format=should_use_chat_format(
            config_format=args.dataset.format,
            dataset_chat_template=args.dataset.chat_template or tokenizer.chat_template,
        ),
    )

    ### --- Training ---
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        task_type=TaskType.CAUSAL_LM,
        bias="none",
        target_modules="all-linear",
    )
    training_args = SFTConfig(
        output_dir=checkpoint_dir,
        num_train_epochs=args.epochs,
        learning_rate=args.learning_rate,
        lr_scheduler_type=args.lr_scheduler_type,
        max_steps=args.max_steps,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_acc_steps,
        max_grad_norm=args.max_grad_norm,
        warmup_ratio=args.warmup_ratio,
        warmup_steps=args.warmup_steps,
        weight_decay=args.weight_decay,
        optim=args.optim,
        save_steps=args.save_steps,
        logging_steps=args.logging_steps,
        bf16=True,
        max_length=args.max_seq_length,
        report_to="mlflow" if mlf.enabled else "none",
    )
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        processing_class=tokenizer,
        args=training_args,
        peft_config=lora_config,
    )
    trainer.train()
    logger.info("✅ Model training completed")

    ### --- Save model ---
    merge_and_write(trainer, tokenizer, args.model_name, output_dir, finetuned_dir)

    ### --- Push model ---
    push_model_to_hf(finetuned_dir, args.hf_push_repo)


@no_type_check
def merge_and_write(trainer: Any, tokenizer: Any, model_name: str, adapters_dir: str, merged_dir: str):
    import torch

    logger.info(f"Start saving model finetuned {model_name}")
    logger.info(f"Start saving adapters to {adapters_dir}...")

    # Save adapters
    trainer.save_model(adapters_dir)
    tokenizer.save_pretrained(adapters_dir)
    logger.info(f"✅ Adapters saved to {adapters_dir}")

    # Free VRAM
    del trainer
    torch.cuda.empty_cache()

    logger.info(f"Start saving merged model to {merged_dir}...")
    try:
        merge_adapters_to_model(
            name_or_path=adapters_dir,
            merged_dir=merged_dir,
            base_model_name_or_path=model_name,
            tokenizer_name_or_path=adapters_dir,
        )
        # mlflow_log_model(model_name, model_merged, tokenizer)

    except Exception as error:
        logger.warning("Adapters are saved, but merge failed.")
        logger.error(f"Failed to merge model: {error}")

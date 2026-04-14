"""
Entrypoint: finetune-causal-unsloth
Finetune a causal LM using Unsloth for optimized 4-bit training.
"""

import os
from typing import no_type_check
from pydantic import BaseModel
from ai_core.datasets.load import load
from ai_core.datasets.convert import construct_prompts
from ai_core.datasets.utils import should_use_conversational_format
from ai_core.models.write import unsloth_merge_and_write
from ai_core.configs.load import load_prompt_config
from ai_core.tracking.client import mlflow_is_enabled
from ai_core.tracking.log import (
    mlflow_log_dataset,
    mlflow_start,
    mlflow_end,
    mlflow_log_tags,
    mlflow_log_params,
)
from ai_core.models.push import push_model_to_hf
from ai_core.utils.files import folder_create
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)

# 4bit pre quantized models we support for 4x faster downloading + no OOMs.
fourbit_models = [
    "unsloth/Meta-Llama-3.1-8B-bnb-4bit",  # Llama-3.1 2x faster
    "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit",
    "unsloth/Meta-Llama-3.1-70B-bnb-4bit",
    "unsloth/Meta-Llama-3.1-405B-bnb-4bit",  # 4bit for 405b!
    "unsloth/Mistral-Small-Instruct-2409",  # Mistral 22b 2x faster!
    "unsloth/mistral-7b-instruct-v0.3-bnb-4bit",
    "unsloth/Phi-3.5-mini-instruct",  # Phi-3.5 2x faster!
    "unsloth/Phi-3-medium-4k-instruct",
    "unsloth/gemma-2-9b-bnb-4bit",
    "unsloth/gemma-2-27b-bnb-4bit",  # Gemma 2x faster!
    "unsloth/Llama-3.2-1B-bnb-4bit",  # NEW! Llama 3.2 models
    "unsloth/Llama-3.2-1B-Instruct-bnb-4bit",
    "unsloth/Llama-3.2-3B-bnb-4bit",
    "unsloth/Llama-3.2-3B-Instruct-bnb-4bit",
    "unsloth/Llama-3.3-70B-Instruct-bnb-4bit",  # NEW! Llama 3.3 70B!
]  # More models at https://huggingface.co/unsloth


def is_unsloth_model(model_name: str, limit_to_4bit: bool = False):
    if limit_to_4bit:
        return model_name in fourbit_models
    return model_name.startswith("unsloth/")


@no_type_check
def run(args: BaseModel, tracking=None, **kwargs):
    """Finetune a causal LM with Unsloth."""
    # GPU imports inside the function to avoid dependencies at import time
    from transformers.data.data_collator import DataCollatorForSeq2Seq

    # unlosth has to be imported before trl see https://stackoverflow.com/questions/79663362/sfttrainer-the-specified-eos-token-eos-token-is-not-found-in-the-vocabu
    from unsloth import FastLanguageModel
    from unsloth.chat_templates import train_on_responses_only
    from trl import SFTConfig, SFTTrainer

    logger.info("Starting pipeline finetune-causal-unsloth...")
    logger.debug(f"with args = {args.model_dump(exclude_defaults=True)}")

    ### --- Start tracking ---
    mlflow_start(
        args.model_name,
        run_type="training",
        tags={"model_name": args.model_name, "dataset_name": args.dataset_name},
    )

    ### --- Setup ---
    model_dir = folder_create(os.path.join("jobs", args.model_name))
    output_dir = os.path.join(model_dir, "output")
    checkpoint_dir = os.path.join(output_dir, "checkpoints")
    finetuned_dir = os.path.join(output_dir, "finetuned")

    ### --- Load prompts config ---
    prompts_cfg = load_prompt_config(args.prompts_config, from_disk=True) if args.prompts_config else None
    if prompts_cfg:
        mlflow_log_tags({"prompts_config": args.prompts_config})
        mlflow_log_params(prompts_cfg)

    ### --- Load model and tokenizer ---
    logger.info(f"Start loading model {args.model_name}")
    if not is_unsloth_model(args.model_name, limit_to_4bit=True):
        raise ValueError(f"Model {args.model_name} is not a valid unsloth 4bit model!")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model_name,
        max_seq_length=args.max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_r,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=69,
        use_rslora=False,
        loftq_config=None,
    )

    logger.debug(f"Model embeddings size: {model.get_input_embeddings().weight.size(0)}")
    logger.debug(f"Tokenizer template: {tokenizer.chat_template}")
    logger.info("✅ Model and tokenizer loaded")

    ### --- Load dataset ---
    dataset = load(args.dataset_name, split=args.dataset_split)
    mlflow_log_dataset(args.dataset_name, dataset, dataset_split=args.dataset_split)
    logger.info("✅ Dataset loaded")

    ### --- Format prompts ---
    dataset = construct_prompts(
        dataset,
        custom_instruction=prompts_cfg.get("instruction"),
        custom_text_format=prompts_cfg.get("text_format"),
        use_conversational_format=should_use_conversational_format(
            dataset_format_arg=prompts_cfg.get("format"),
            dataset_chat_template=tokenizer.chat_template,
        ),
    )

    ### --- Training ---
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
        report_to="mlflow" if mlflow_is_enabled() else "none",
    )
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        processing_class=tokenizer,
        args=training_args,
        data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer),
    )
    if prompts_cfg.get("instruction_part") and prompts_cfg.get("response_part"):
        trainer = train_on_responses_only(
            trainer,
            instruction_part=prompts_cfg.get("instruction_part"),
            response_part=prompts_cfg.get("response_part"),
        )
        logger.warning("⚠️ Training model on responses only enabled!")
    trainer.train()
    logger.info("✅ Model training completed")

    ### --- Save model ---
    unsloth_merge_and_write(trainer, tokenizer, args.model_name, finetuned_dir)

    ### --- Push model ---
    push_model_to_hf(finetuned_dir)

    ### --- Finalize ---
    mlflow_end()
    logger.info("Pipeline completed.")

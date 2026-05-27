"""
Entrypoint: finetune-causal-unsloth
Finetune a causal LM using Unsloth for optimized 4-bit training.
"""

import os
from typing import no_type_check
from pydantic import BaseModel
from ai_core.datasets.load import load
from ai_core.datasets.convert import construct_prompts, rename_columns
from ai_core.datasets.utils import should_use_chat_format
from ai_core.models.write import unsloth_merge_and_write
from ai_core.tracking.client import mlflow_is_enabled
from ai_core.tracking.log import mlflow_log_dataset, mlflow_start, mlflow_end
from ai_core.models.push import push_model_to_hf
from ai_core.utils.files import folder_create
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)

def is_unsloth_model(model_name: str, limit_to_4bit: bool = False):
    if limit_to_4bit:
        if not model_name.endswith("-4bit"):
            return False
    return model_name.startswith("unsloth/")

@no_type_check
def run(args: BaseModel, **kwargs):
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
        tags={"model_name": args.model_name, "dataset_name": args.dataset.path},
    )

    ### --- Setup ---
    model_dir: str = folder_create(os.path.join("jobs", args.model_name))
    output_dir = os.path.join(model_dir, "output")
    checkpoint_dir = os.path.join(output_dir, "checkpoints")
    finetuned_dir = os.path.join(output_dir, "finetuned")

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
    dataset = load(args.dataset.path, split=args.dataset.split)
    mlflow_log_dataset(args.dataset.path, dataset, dataset_split=args.dataset.split)
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
    if args.dataset.instruction_part and args.dataset.response_part:
        trainer = train_on_responses_only(
            trainer,
            instruction_part=args.dataset.instruction_part,
            response_part=args.dataset.response_part,
        )
        logger.warning("⚠️ Training model on responses only enabled!")
    trainer.train()
    logger.info("✅ Model training completed")

    ### --- Save model ---
    unsloth_merge_and_write(trainer, tokenizer, args.model_name, finetuned_dir)

    ### --- Push model ---
    push_model_to_hf(finetuned_dir, args.hf_push_repo)

    ### --- Finalize ---
    mlflow_end()
    logger.info("Pipeline completed.")

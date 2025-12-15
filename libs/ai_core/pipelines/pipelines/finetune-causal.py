import os
from pydantic import BaseModel
from typing import Optional
from ai_core.pipelines.registry import register_pipeline_cloud, PipelineRegistryCloud
from ai_core.datasets.load import load
from ai_core.datasets.convert import construct_prompts
from ai_core.datasets.utils import should_use_conversational_format
from ai_core.cloud.schemas import CloudJobInfrastructure
from ai_core.configs.load import load_prompt_config
from ai_core.tracking.log import (
    mlflow_log_dataset,
    mlflow_log_model,
    mlflow_start,
    mlflow_end,
    mlflow_log_tags,
    mlflow_log_params,
)
from ai_core.tracking.client import mlflow_is_enabled
from ai_core.utils.files import folder_create
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineArgs(BaseModel):
    model_name: str
    dataset_name: str
    dataset_split: Optional[str]

    # Config
    prompts_config: Optional[str]

    # Lora args
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05

    # Training args
    max_seq_length: int = 2048
    epochs: int = 3
    max_steps: int = -1
    batch_size: int = 1
    grad_acc_steps: int = 4
    optim: str = "paged_adamw_8bit"
    learning_rate: float = 2e-5
    lr_scheduler_type: str = "linear"
    weight_decay: float = 0.001
    max_grad_norm: float = 0.3
    warmup_ratio: float = 0.03
    save_steps: int = 500
    logging_steps: int = 50


pipeline = PipelineRegistryCloud(
    pipeline="finetune-causal",
    args=PipelineArgs,
    infrastructure=CloudJobInfrastructure(
        image="ghcr.io/ml-hub/cuda-base:latest",
        volumes=["llm-jobs@1azgra/:/workspace/jobs:RWD", "llm-datasets@1azgra/:/workspace/datasets:RO"],
    ),
    description="Finetune a causal model",
    tags=["finetuning", "transformers", "lora", "bitandbytes"],
)


@register_pipeline_cloud(pipeline)
def finetune_causal(args: PipelineArgs):
    # GPU imports should be inside the function to avoid dependencies
    # Make sure selected packages are included in the cloud image
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig, AutoPeftModelForCausalLM, TaskType, prepare_model_for_kbit_training
    from trl import SFTConfig, SFTTrainer

    logger.info(f"Starting pipeline finetune-causal...")
    logger.debug(f"with args = {args.model_dump()}")

    # Start tracking
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

    ### --- Config ---
    prompts_cfg = load_prompt_config(args.prompts_config) if args.prompts_config else None
    if prompts_cfg:
        mlflow_log_tags({"prompts_config": args.prompts_config})
        mlflow_log_params(prompts_cfg)

    ### --- Load model ---
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
    logger.info(f"✅ Model and tokenizer loaded")

    ### --- Load dataset ---
    dataset = load(args.dataset_name, split=args.dataset_split)
    mlflow_log_dataset(args.dataset_name, dataset, dataset_split=args.dataset_split)
    logger.info(f"✅ Dataset loaded")

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
        weight_decay=args.weight_decay,
        optim=args.optim,
        save_steps=args.save_steps,
        logging_steps=args.logging_steps,
        bf16=True,
        # group_by_length=False,
        # packing=False,
        max_length=args.max_seq_length,
        report_to="mlflow" if mlflow_is_enabled() else "none",
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
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    logger.info(f"✅ Adapters saved to {output_dir}")

    # Free VRAM
    del trainer
    torch.cuda.empty_cache()

    try:
        # Merge model
        logger.debug("Merging: Loading PEFT model...")
        peft_model = AutoPeftModelForCausalLM.from_pretrained(
            output_dir,
            device_map="auto",
            dtype=torch.bfloat16,  # Must be 16-bit for merging
            low_cpu_mem_usage=True,
        )
        model_merged = peft_model.merge_and_unload()

        # Save merged model
        model_merged.save_pretrained(finetuned_dir, safe_serialization=True)
        tokenizer.save_pretrained(finetuned_dir)

        logger.info(f"✅ Model merged and saved to {finetuned_dir}")
        mlflow_log_model(args.model_name, model_merged, tokenizer)

    except Exception as error:
        logger.warning("Adapters are saved, but merge failed.")
        logger.error(f"Failed to merge model: {error}")

    mlflow_end()
    logger.info(f"Pipeline completed.")

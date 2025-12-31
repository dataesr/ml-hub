import os
from pydantic import BaseModel
from typing import Optional
from ai_core.pipelines.registry import register_pipeline_cloud, PipelineRegistryCloud
from ai_core.datasets.load import load
from ai_core.datasets.convert import construct_prompts
from ai_core.datasets.utils import should_use_conversational_format
from ai_core.cloud.schemas import CloudJobInfrastructure, CloudJobVolume
from ai_core.cloud.constants import CONFIGS_CONTAINER, DATASETS_CONTAINER, JOBS_CONTAINER
from ai_core.configs.load import load_prompt_config
from ai_core.tracking.client import mlflow_is_enabled
from ai_core.tracking.log import (
    mlflow_log_dataset,
    mlflow_start,
    mlflow_end,
    mlflow_log_tags,
    mlflow_log_params,
)
from ai_core.tracking.schemas import TrackingConfig
from ai_core.models.write import merge_and_write
from ai_core.models.push import push_model_to_hf
from ai_core.utils.files import folder_create
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineArgs(BaseModel):
    model_name: str
    dataset_name: str
    dataset_split: str = "train"

    # Config
    prompts_config: Optional[str] = None

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
    description="Finetune a causal model",
    tags=["finetuning", "causallm", "transformers", "lora", "bitandbytes"],
    args=PipelineArgs,
    infrastructure=CloudJobInfrastructure(
        image="ghcr.io/dataesr/ml-hub/cuda-base:latest",
        name="finetune-causallm",
        command=["ai-pipeline-run"],
        volumes=[
            CloudJobVolume(container=CONFIGS_CONTAINER, mount="configs"),
            CloudJobVolume(container=DATASETS_CONTAINER, mount="datasets"),
            CloudJobVolume(container=JOBS_CONTAINER, mount="jobs", permission="RWD"),
        ],
    ),
    tracking=TrackingConfig(),  # default tracking config
)

@register_pipeline_cloud(pipeline)
def finetune_causal(args: PipelineArgs):
    # GPU imports should be inside the function to avoid dependencies
    # Make sure selected packages are included in the cloud image
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig, TaskType, prepare_model_for_kbit_training
    from trl import SFTConfig, SFTTrainer

    logger.info("Starting pipeline finetune-causal...")
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
    merge_and_write(trainer, tokenizer, args.model_name, output_dir, finetuned_dir)

    ### --- Push model ---
    push_model_to_hf(finetuned_dir)

    ### --- Finalize ---
    mlflow_end()
    logger.info("Pipeline completed.")

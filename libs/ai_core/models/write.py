from typing import Any
from ai_core.tracking.log import mlflow_log_model
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


def merge_and_write(trainer: Any, tokenizer: Any, model_name: str, adapters_dir: str, merged_dir: str):
    import torch
    from peft import AutoPeftModelForCausalLM

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
        # Merge model
        logger.debug("Merging: Loading PEFT model...")
        peft_model = AutoPeftModelForCausalLM.from_pretrained(
            adapters_dir,
            device_map="auto",
            dtype=torch.bfloat16,  # Must be 16-bit for merging?
            low_cpu_mem_usage=True,
        )
        model_merged = peft_model.merge_and_unload()

        # Save merged model
        model_merged.save_pretrained(merged_dir, safe_serialization=True)
        tokenizer.save_pretrained(merged_dir)

        logger.info(f"✅ Model merged and saved to {merged_dir}")
        mlflow_log_model(model_name, model_merged, tokenizer)

    except Exception as error:
        logger.warning("Adapters are saved, but merge failed.")
        logger.error(f"Failed to merge model: {error}")


def unsloth_merge_and_write(trainer, tokenizer, model_name: str, merged_dir: str):
    import torch

    logger.info(f"Start saving finetuned model {model_name}")

    # Get model from trainer
    model = trainer.model.module if hasattr(trainer.model, "module") else trainer.model

    # Free VRAM
    del trainer
    torch.cuda.empty_cache()

    # Save merged model as 16 bit
    logger.info(f"Start saving merged model to {merged_dir}...")
    model.save_pretrained_merged(save_directory=merged_dir, tokenizer=tokenizer, save_method="merged_16bit")
    logger.info(f"✅ Model merged and saved to {merged_dir}")
    mlflow_log_model(model_name, model, tokenizer)

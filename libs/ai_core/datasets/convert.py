from datasets import Dataset
from ai_core.datasets.constants import (
    CONVERSATIONS_COLUMN,
    TEXT_COLUMN,
    INSTRUCTION_COLUMN,
    INPUT_COLUMN,
    OUTPUT_COLUMN,
    DEFAULT_TEXT_FORMAT,
)
from ai_core.utils.logger import get_logger

logger = get_logger(__name__)


def construct_one_conversation(user: str, system: str | None = None, assistant: str | None = None):
    """
    Construct a conversation from system, user and assistant messages

    Args:
    - user (str): user input
    - system (str, optional): system instructions. Defaults to None.
    - assistant (str, optional): assistant completion for training. Defaults to None.

    Returns a conversation object
    """
    conversation = []

    # Add system prompt
    if system:
        conversation.append({"role": "system", "content": system})

    # Add user prompt
    conversation.append({"role": "user", "content": user})

    # Add assistant prompt
    if assistant:
        conversation.append({"role": "assistant", "content": assistant})

    return conversation


def construct_prompts(
    dataset: Dataset,
    custom_instruction: str | None = None,
    custom_text_format: str | None = None,
    use_conversational_format: bool = False,
) -> Dataset:
    """
    Construct prompts for training on a dataset

    Args:
    - dataset (Dataset): training dataset
    - custom_instruction (str): custom system prompt
    - custom_text_format (str): custom text format
    - use_conversational_format (bool): Use conversational or text format
    Returns the a dataset with the prompt column (either conversational or text)
    """
    prompts_field = CONVERSATIONS_COLUMN if use_conversational_format else TEXT_COLUMN

    def map_conversations(example):
        if use_conversational_format:
            # Conversational format (list of messages, ChatML-like)
            return {
                prompts_field: construct_one_conversation(
                    system=custom_instruction or example.get(INSTRUCTION_COLUMN),
                    user=example[INPUT_COLUMN],
                    assistant=example[OUTPUT_COLUMN],
                )
            }
        else:
            # Non-conversational (Alpaca-style prompt-response text)
            instruction = custom_instruction or "You are an helpful assistant."
            text_format = custom_text_format or DEFAULT_TEXT_FORMAT
            text = text_format.format(instruction=instruction, input=example[INPUT_COLUMN], response=example[OUTPUT_COLUMN])
            return {prompts_field: text}

    dataset = dataset.map(map_conversations).select_columns([prompts_field])  # keep only the formatted column
    logger.debug(f"✅ Dataset formatted with {'conversation' if use_conversational_format else 'text'} format")
    logger.debug(f"Dataset columns: {dataset.column_names}")
    logger.debug(f"Dataset sample: {dataset[0][prompts_field]}")
    return dataset

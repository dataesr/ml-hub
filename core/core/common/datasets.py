"""
Datasets utils.
"""

import os
from datasets import Dataset, load_dataset
from core.common.ovh import ovhai_object_download, DATASETS_CONTAINER, DATASETS_VOLUME
from core.utils.logger import get_logger

logger = get_logger(__name__)

TEXT_COLUMN = "text"
CONVERSATIONS_COLUMN = "messages"  # read by sft trainer
INSTRUCTION_COLUMN = "instruction"
INPUT_COLUMN = "input"
OUTPUT_COLUMN = "completion"

DEFAULT_TEXT_FORMAT = "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n{response}"


def load_from_ovh(path: str, container: str) -> Dataset:
    file_path = ovhai_object_download(path, container)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Error while downloading {path}")
    dataset = load_dataset("json", data_files={"file": [file_path]}, split="file")
    os.remove(file_path)
    return dataset


def load_from_local(path: str) -> Dataset:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File {path} not found on disk")
    dataset = load_dataset("json", data_files={"file": [path]}, split="file")
    return dataset


def load_from_hf(dataset_name: str, split: str | None = None) -> Dataset:
    dataset: Dataset = load_dataset(dataset_name, split=split)  # ty:ignore[invalid-assignment]
    return dataset


def load(path_or_name: str, split: str | None = None) -> Dataset:
    try:
        logger.debug(f"Trying to load {path_or_name} from HuggingFace...")
        dataset = load_from_hf(path_or_name, split=split)
    except Exception as error:
        logger.debug(f"Error while loading from HuggingFace: {error}")
        try:
            logger.debug("Trying to load from local storage...")
            local_path = os.path.join(DATASETS_VOLUME, path_or_name)
            dataset = load_from_local(local_path)
        except Exception as error:
            logger.debug(f"Error while loading from local storage: {error}")
            try:
                logger.debug("Trying to load from ovh...")
                dataset = load_from_ovh(path_or_name, container=DATASETS_CONTAINER)
            except Exception as error:
                logger.error(f"Error while loading from ovh: {error}")
                raise Exception(f"Failed to load dataset {path_or_name}")

    if dataset:
        logger.debug(f"✅ Dataset {path_or_name} loaded!")
        logger.debug(f"Dataset schema: {dataset.features}")
        logger.debug(f"Dataset size: {len(dataset)}")
        logger.debug(f"Dataset sample: {dataset[0]}")
    else:
        logger.error(f"Error while loading {path_or_name}")
        raise Exception(f"Error while loading {path_or_name}")

    return dataset


def construct_one_prompt(
    input: str, instruction: str | None = None, response: str | None = None, text_format: str | None = None
):
    """
    Construct a prompt from system, user and assistant messages

    Args:
    - input (str): user input
    - instruction (str, optional): system instructions. Defaults to None.
    - assistant (str, optional): assistant completion for training. Defaults to None.
    - text_format (str, optional): custom text format. Defaults to None.

    Returns a prompt string
    """
    if text_format is None:
        text_format = DEFAULT_TEXT_FORMAT

    logger.debug(f"{text_format=} {input=}")
    prompt = text_format.format(instruction=instruction or "", input=input, response=response or "")
    # logger.debug(f"prompt = {prompt}")
    return prompt


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
    use_chat_format: bool = False,
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
    prompts_field = CONVERSATIONS_COLUMN if use_chat_format else TEXT_COLUMN

    def map_conversations(example):
        if use_chat_format:
            # Conversational format (list of messages, ChatML-like)
            return {
                prompts_field: construct_one_conversation(
                    system=custom_instruction or example.get(INSTRUCTION_COLUMN),
                    user=example[INPUT_COLUMN],
                    assistant=example[OUTPUT_COLUMN] if OUTPUT_COLUMN in example else None,
                )
            }
        else:
            # Non-conversational (Alpaca-style prompt-response text)
            instruction = custom_instruction if custom_instruction is not None else "You are an helpful assistant."
            text_format = custom_text_format or DEFAULT_TEXT_FORMAT
            text = text_format.format(
                instruction=instruction,
                input=example[INPUT_COLUMN],
                response=example[OUTPUT_COLUMN] if OUTPUT_COLUMN in example else "",
            )
            return {prompts_field: text}

    dataset = dataset.map(map_conversations).select_columns([prompts_field])  # keep only the formatted column
    logger.debug(f"✅ Dataset formatted with {'chat' if use_chat_format else 'text'} format")
    logger.debug(f"Dataset columns: {dataset.column_names}")
    logger.debug(f"Dataset sample: {dataset[0][prompts_field]}")
    return dataset


def rename_columns(
    dataset: Dataset, instruction_col: str | None = None, input_col: str | None = None, output_col: str | None = None
) -> Dataset:
    """
    Rename a dataset with default column names

    Args:
    - dataset (Dataset): input dataset
    - instruction_col (str): custom name of the instruction column
    - input_col (str): custom name of the input column
    - output_col (str): custom name of the output column
    Returns a dataset with the expected INSTRUCTION_COLUMN, INPUT_COLUMN and OUTPUT_COLUMN
    """

    if instruction_col and instruction_col in dataset.column_names:
        dataset: Dataset = dataset.rename_column(instruction_col, INSTRUCTION_COLUMN)
    if input_col and input_col in dataset.column_names:
        dataset: Dataset = dataset.rename_column(input_col, INPUT_COLUMN)
    if output_col and output_col in dataset.column_names:
        dataset: Dataset = dataset.rename_column(output_col, OUTPUT_COLUMN)
    return dataset


def get_commit_hash(dataset: Dataset) -> str | None:
    """
    Retrieve commit hash from dataset checksums

    Args:
        dataset (Dataset): dataset

    Returns:
        commit_hash (str): dataset commit hash
    """
    commit_hash = None

    if not isinstance(dataset, Dataset):
        return commit_hash

    checksums = dataset.info.download_checksums
    if isinstance(checksums, dict) and checksums:
        checksums_list = list(checksums.keys())
        checksum_file = checksums_list[0].split("@")[1]  # ty:ignore[unresolved-attribute]
        commit_hash = checksum_file.split("/")[0]
    return commit_hash


def get_prompts(data: Dataset) -> list[str]:
    input_col = INPUT_COLUMN
    if input_col not in data.column_names:
        raise ValueError(f"Column {input_col} not found on data! Set env var 'INPUT_COLUMN' to select the column name.")

    prompts = list(data[input_col])
    return prompts


def should_use_chat_format(config_format: str | None = None, dataset_chat_template=None):
    if config_format == "chat":
        logger.debug("Format set to 'chat'")
        return True
    elif config_format == "text":
        logger.debug("Format set to 'text'")
        return False
    else:
        if dataset_chat_template is not None:
            logger.debug("Format automatically set to 'chat'")
            return True
        else:
            logger.debug("Format automatically set to 'text'")
            return False

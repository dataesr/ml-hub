from typing import Literal

# --- Storage containers ---
CONFIGS_CONTAINER = "llm-configs"
DATASETS_CONTAINER = "llm-datasets"

# --- Dataset and column standards ---
TEXT_COLUMN = "text"
CONVERSATIONS_COLUMN = "messages"  # read by sft trainer
INSTRUCTION_COLUMN = "instruction"
INPUT_COLUMN = "input"
OUTPUT_COLUMN = "completion"

DEFAULT_TEXT_FORMAT = "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n{response}"

# --- Compute  ---
COMPUTE_GPU = "l4-1-gpu"
JOB_STATE = Literal[
    "QUEUED",
    "PENDING",
    "INITIALIZING",
    "FINALIZING",
    "RUNNING",
    "TIMEOUT",
    "FAILED",
    "ERROR",
    "DONE",
    "INTERRUPTED",
    "INTERRUPTING",
    "SYNC_FAILED",
]
APP_STATE = Literal[
    "QUEUED",
    "PENDING",
    "INITIALIZING",
    "SCALING",
    "RUNNING",
    "STOPPING",
    "STOPPED",
    "FAILED",
    "ERROR",
]

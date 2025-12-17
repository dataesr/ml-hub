from typing import Literal

# --- containers ---
CONTAINERS_REGION = "1azgra"
CONFIGS_CONTAINER = "llm-configs"
DATASETS_CONTAINER = "llm-datasets"
JOBS_CONTAINER = "llm-jobs"
COMPLETIONS_CONTAINER = "llm-completions"

# --- volumes ---
VOLUMES_PERMISSIONS = Literal["RO", "RW", "RWD"]  # read-only / read-write / read-write-delete

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

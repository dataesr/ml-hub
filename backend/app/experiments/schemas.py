from typing import Literal


RUN_STATES = Literal["crashed", "failed", "finished", "killed", "running", "pending"]
ARTIFACT_TYPES = Literal["model", "dataset"]

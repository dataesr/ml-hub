import os
from typing import Literal
import wandb
from wandb import Api as wb
from app.logger import get_logger

logger = get_logger(__name__)

RUN_STATES = Literal["crashed", "failed", "finished", "killed", "running", "pending"]

wb = wandb.Api()


def wandb_list_projects(entity: str):
    projects = wb.projects(entity=entity)
    projects = [project._attrs for project in projects]
    return projects


def wandb_list_runs(entity: str, project: str, state: RUN_STATES = None):
    runs = wb.runs(f"{entity}/{project}")
    runs = [
        {"id": run.id, "name": run.name, "displayName": run.displayName, "state": run.state, "createdAt": run.createAt}
        for run in runs
    ]
    if state:
        runs = [run for run in runs if run["state"] == state]
    return runs

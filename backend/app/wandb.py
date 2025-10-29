import os
import wandb
from app.logger import get_logger

logger = get_logger(__name__)

wandb.login(key=os.getenv("WANDB_KEY"))
wb = wandb.Api(api_key=os.getenv("WANDB_KEY"))

client = wb.client
logger.debug(f"api_key={os.getenv('WANDB_KEY')}")
logger.debug(f"{client.__dict__=}")


def wandb_list_projects(entity: str):
    projects = wb.projects(entity=entity)
    logger.debug(f"{projects=}")
    logger.debug(f"{projects.__dict__}")
    return projects.objects


def wandb_list_runs(entity: str, project: str):
    # runs = wb.runs(f"{entity}/{project}")
    # return runs
    return {"ok": 0}

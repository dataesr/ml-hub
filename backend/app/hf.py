import os
from huggingface_hub import list_models, model_info
from app.logger import get_logger

logger = get_logger(__name__)


def hf_model_info(model_id: str):
    model = model_info(repo_id=model_id)
    return model.__dict__


def hf_list_models(owner: str = None, limit: int = 100):
    models = list_models(author=owner, limit=limit, fetch_config=True)
    models = [model.__dict__ for model in models]
    # logger.debug(f"{models =}")
    return models

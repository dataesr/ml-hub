import time
from ai_core.utils.types import ENV

def env_exist(envs: list[ENV], env_name: str, env_value: str):
    for env in envs:
        if env.name == env_name and env.value == env_value:
            return True
    return False


def timestamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

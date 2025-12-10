from ai_core.schemas.types import ENV

def env_exist(envs: list[ENV], env_name: str, env_value: str):
    for env in envs:
        if env["name"] == env_name and env["value"] == env_value:
            return True
    return False

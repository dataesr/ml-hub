from fastapi import APIRouter
from ai_core.configs.load import load_yaml_config
from ai_core.configs.write import write_yaml_config
from ai_core.configs.list import list_configs

router = APIRouter(tags=["configs"])


@router.get("/configs")
def configs_list(type: str | None = None):
    configs = list_configs(type)
    return configs


@router.post("/configs")
def configs_add(data: dict):  # type input
    cfg_name = data.pop("name")
    cfg_type = data.pop("type")
    cfg = data.pop("data")
    write_yaml_config(cfg, cfg_name, cfg_type)
    return {f"{cfg_name}": "config uploaded"}


@router.get("/configs/{name}")
def configs_get(name: str, type: str):
    config = load_yaml_config(name, type)
    return config

from fastapi import APIRouter
from core.configs.load import load_yaml_config
from core.configs.write import write_yaml_config
from core.configs.list import list_configs

router = APIRouter(tags=["configs"])


@router.get("/configs")
def configs_list():
    configs = list_configs()
    return configs


@router.post("/configs")
def configs_add(data: dict):  # type input
    cfg_name = data.pop("name")
    cfg = data.pop("data")
    write_yaml_config(cfg, cfg_name)
    return {f"{cfg_name}": "config uploaded"}


@router.get("/configs/{name}")
def configs_get(name: str):
    config = load_yaml_config(name)
    return config

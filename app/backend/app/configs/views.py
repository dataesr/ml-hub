from fastapi import APIRouter
from app.configs import service as cfg_svc

router = APIRouter(tags=["configs"])


@router.get("/configs")
def configs_list(dataset_name: str = None):
    configs = cfg_svc.list_all(dataset_name)
    return configs


@router.post("/configs")
def configs_add(config: dict):
    cfg_name = config.pop("name")
    cfg_type = config.pop("type")
    cfg_svc.add(config, cfg_name, cfg_type)
    return {f"{cfg_name}": "config uploaded"}


@router.get("/configs/{name}")
def configs_get(name: str, type: str):
    config = cfg_svc.get(name, type)
    return config

import os
from fastapi import APIRouter, HTTPException
from core.common.configs import load_yaml_config, write_yaml_config

router = APIRouter(tags=["configs"])

CONFIG_DIR = "configs/jobs"


@router.get("/configs")
def configs_list(data: bool = False):
    files = os.listdir(CONFIG_DIR)
    configs = [file[:-5] for file in files if file.endswith(".yaml")]
    if data:
        configs = {name: load_yaml_config(os.path.join(CONFIG_DIR, f"{name}.yaml")) for name in configs}
    return configs


# @router.post("/configs")
# def configs_add(data: dict):  # type input
#     cfg_name = str(data.pop("name") or "").strip()
#     cfg_path = os.path.join(CONFIG_DIR, f"{cfg_name}.yaml")

#     if os.path.exists(cfg_path):
#         raise HTTPException(status_code=404, detail=f"Config '{cfg_name}' already exists. Use a different name.")

#     cfg = data.pop("data")
#     write_yaml_config(cfg, cfg_path)
#     return {cfg_name: "config uploaded"}


@router.get("/configs/{name}")
def configs_get(name: str):
    cfg_path = os.path.join(CONFIG_DIR, f"{name}.yaml")
    config = load_yaml_config(cfg_path)
    return config

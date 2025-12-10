from ai_core.configs.load import load_yaml_config
from ai_core.configs.write import write_yaml_config
from ai_core.configs.list import list_configs


def list_all(cfg_type: str = None):
    configs = list_configs(cfg_type)
    return configs


def get(cfg_name: str, cfg_type: str):
    cfg = load_yaml_config(cfg_name, cfg_type)
    return cfg


def add(data: dict):
    cfg_name = data.pop("name")
    cfg_type = data.pop("type")
    cfg = data.pop("data")
    write_yaml_config(cfg, cfg_name, cfg_type)
    return cfg_name

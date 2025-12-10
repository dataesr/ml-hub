from ai_core.configs.loaders import load_yaml_config
from ai_core.configs.writers import write_yaml_config
from ai_core.configs.utils import list_configs


def list_all(cfg_type: str = None):
    configs = list_configs(cfg_type)
    return configs


def get(cfg_name: str, cfg_type: str):
    cfg = load_yaml_config(cfg_name, cfg_type)
    return cfg


def add(data: dict, cfg_name: str, cfg_type: str):
    write_yaml_config(data, cfg_name, cfg_type)

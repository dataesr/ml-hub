from ai_core.cloud.storage import ovhai_object_list
from ai_core.cloud.constants import CONFIGS_CONTAINER


def list_configs():
    objects = ovhai_object_list(CONFIGS_CONTAINER)
    configs = []
    for obj in objects:
        key: str = obj.get("key", "")

        if not key or not key.endswith(".yaml"):
            continue

        config_name = key.split("/")[-1].removesuffix(".yaml")
        configs.append(
            {
                "config_name": config_name,
                "storage_path": key,
                "size": obj.get("size"),
                "last_modified": obj.get("last_modified"),
            }
        )
    return configs

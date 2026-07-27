import time
import importlib.util
from typing import Any, Optional
from pydantic import create_model, BaseModel

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


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge two dicts. Override values take priority."""
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def import_file_as_module(file_path: str):
    spec = importlib.util.spec_from_file_location(file_path.strip(), file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load file_path: {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_cls_with_defaults(
    base_cls: type[BaseModel],
    instance: BaseModel,
    model_name: str,
) -> type[BaseModel]:
    """
    Build a variant of *base_cls* where every field that was set on *instance*
    becomes a default.  Unset fields keep their original definition.
    """

    fields: dict[str, tuple[Any, Any]] = {}
    set_values = instance.model_dump(exclude_unset=True)
    for name, field_info in base_cls.model_fields.items():
        if name in set_values:
            fields[name] = (Optional[field_info.annotation], set_values[name])
        else:
            fields[name] = (field_info.annotation, field_info)
    return create_model(model_name, __base__=base_cls, **fields)

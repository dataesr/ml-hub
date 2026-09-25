import time
import importlib.util
from typing import Any, Optional
from pydantic import create_model, BaseModel

def timestamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def dict_to_dotted(d: dict[str, Any], parent_key: str = "", sep: str = ".") -> dict[str, Any]:
    """Flatten nested dictionaries into dotted keys while preserving lists."""
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(dict_to_dotted(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def dotted_to_dict(items: list[tuple[str, Any]], sep: str = ".") -> dict[str, Any]:
    """Expand dotted keys into nested dictionaries, grouping repeated keys as lists."""
    result: dict[str, Any] = {}
    for key, value in items:
        current = result
        parts = key.split(sep)
        for part in parts[:-1]:
            nested = current.get(part)
            if not isinstance(nested, dict):
                nested = {}
                current[part] = nested
            current = nested

        leaf = parts[-1]
        if leaf not in current:
            current[leaf] = value
        elif isinstance(current[leaf], list):
            current[leaf].append(value)
        else:
            current[leaf] = [current[leaf], value]
    return result


def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Backward-compatible alias for :func:`dict_to_dotted`."""
    return dict_to_dotted(d, parent_key, sep)


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

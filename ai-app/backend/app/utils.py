import json
import os
import time
from typing import Any
from app.logger import get_logger

logger = get_logger(__name__)


def json_write(path: str, data: dict[str, Any]):
    json_path = path
    if not json_path.endswith(".json"):
        json_path += ".json"

    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    logger.info(f"JSON file {json_path} saved")

    return json_path


def json_read(path: str, remove: bool = False) -> dict[str, Any]:
    json_path = path
    if not json_path.endswith(".json"):
        json_path += ".json"

    if not os.path.isfile(json_path):
        raise FileNotFoundError(f"JSON file {json_path} not found")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if remove:
        os.remove(json_path)

    return data

def timestamp(print_time: bool = True) -> str:
    if not print_time:
        return time.strftime("%Y%m%d")
    return time.strftime("%Y%m%d-%H%M%S")

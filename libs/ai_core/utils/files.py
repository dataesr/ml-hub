import os
import yaml
import json


def file_create_directory(path: str):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    return


def file_write_yaml(path: str, content: dict):
    file_create_directory(path)
    with open(path, "w", encoding="utf-8") as file:
        yaml.safe_dump(content, file, sort_keys=False)


def file_write_json(path: str, content: dict):
    file_create_directory(path)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(content, file)

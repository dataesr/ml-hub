import os
import shutil
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


def folder_reset(path: str, delete: bool = False):
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        return

    if not delete:
        os.makedirs(path)


def folder_create(path: str, override: bool = False):
    """
    Create a directory with smart handling of existing paths.

    Args:
        dir_path (str): The directory path to create
        override (bool): If True, override existing non-empty directory

    Returns:
        str: The actual path that was created

    Behavior:
        - Creates directory if path doesn't exist (including nested paths)
        - Does nothing if path exists and is empty
        - Creates directory with different name if path exists and is non-empty
        - Overrides existing directory if override=True
    """
    # Create dir if path doesnt exist
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        return dir_path

    # Folder exists
    if os.path.isdir(dir_path):

        # Folder is empty
        if not os.listdir(dir_path):
            return dir_path

        # Folder not empty - override
        if override:
            reset_folder(dir_path)
            return dir_path

        # Folder not empty - create with different name
        counter = 1
        while True:
            new_dir_path = f"{dir_path}_{counter}"
            if not os.path.exists(new_dir_path):
                os.makedirs(new_dir_path)
                return new_dir_path
            counter += 1

    # force creation by default
    reset_folder(dir_path)
    return dir_path

import os
import json
from fastapi import APIRouter, HTTPException
from app.ovhai import DATA_STORE, cmd_run, ovhai_object_delete, ovhai_object_upload

CONTAINERS_PREFIX = "llm-"

router = APIRouter()


def check_authorized_container(container: str):
    if not container.startswith(CONTAINERS_PREFIX):
        raise HTTPException(status_code=401, detail="Only 'llm-*' containers access is authorized!")


@router.get("/storage")
def storage_list():
    cmd = f"ovhai bucket list -o json {DATA_STORE}"
    try:
        data = cmd_run(cmd, capture_json=True)
        return data
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/objects/{container}")
def objects_list(container: str):
    check_authorized_container(container)
    cmd = f"ovhai bucket object list -o json {container}@{DATA_STORE}"
    try:
        data = cmd_run(cmd, capture_json=True)
        return data
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/objects/upload_json")
def objects_upload_json(content: dict, file_path: str, container: str, prefix: str = None):
    check_authorized_container(container)
    tmp_path = f"/tmp/{file_path}"
    if not tmp_path.endswith(".json"):
        tmp_path += ".json"
    with open(tmp_path, "w") as f:
        json.dump(content, f)
    try:
        ovhai_object_upload(tmp_path, container, prefix)
        os.remove(tmp_path)
        return {f"{file_path}": "uploaded"}
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/objects/delete")
def objects_delete(object_name: str, container: str):
    check_authorized_container(container)
    try:
        ovhai_object_delete(object_name, container)
        return {f"{object_name}": "deleted"}
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

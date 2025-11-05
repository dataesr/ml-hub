from fastapi import APIRouter, HTTPException
from app.datasets import service as datasets_svc

router = APIRouter()


@router.get("/datasets")
@router.get("/datasets/{owner}")
def datasets_list(owner: str = datasets_svc.OWNER, limit: int = 100):
    try:
        datasets = datasets_svc.list(owner, limit)
        return datasets
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/datasets/{owner}/{name}")
def datasets_get(owner: str, name: str):
    try:
        dataset = datasets_svc.get(owner, name)
        return dataset
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/datasets/configs")
def datasets_configs_list():
    try:
        configs = datasets_svc.list_configs()
        return configs
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/datasets/configs/{name}")
def datasets_configs_get(name: str):
    try:
        config = datasets_svc.get_config(name)
        return config
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


# @router.post("/datasets/configs")
# def datasets_configs_add(config: Config):
#     try:
#         configs = datasets_svc.add_config(config)
#         return configs
#     except Exception as error:
#         raise HTTPException(status_code=400, detail=str(error))


# @router.get("/datasets/configs/{name}")
# def datasets_configs_get_from_storage():
#     try:
#         config = ovhai_object_get()

# @router.post("/datasets/configs")
# def datasets_configs_add_to_storage(name: str):
#     tmp_path = f"/tmp/{name}"
#     if not tmp_path.endswith(".json"):
#         tmp_path += ".json"
#     with open(tmp_path, "w") as f:
#         json.dump(content, f)
#     try:

#         ovhai_object_upload(name, )

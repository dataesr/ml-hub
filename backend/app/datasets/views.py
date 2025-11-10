from fastapi import APIRouter, HTTPException
from app.datasets import service as datasets_svc
from app.datasets.schemas import DatasetConfig

router = APIRouter()


@router.get("/datasets")
@router.get("/datasets/{owner}")
def datasets_list(owner: str = datasets_svc.OWNER, limit: int = 100):
    try:
        datasets = datasets_svc.get_all(owner, limit)
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


# TODO: rename configs routes; not really explicit
@router.get("/configs")
def datasets_configs_list():
    try:
        configs = datasets_svc.list_configs()
        return configs
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/configs")
def datasets_configs_add(config: DatasetConfig):
    try:
        datasets_svc.add_config(config)
        return {f"{config.name}": "config uploaded"}
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/configs/{name}")
def datasets_configs_get(name: str):
    try:
        config = datasets_svc.get_config(name)
        return config
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))

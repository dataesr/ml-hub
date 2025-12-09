from fastapi import APIRouter, HTTPException
from app.datasets import service as datasets_svc
from app.datasets.schemas import DatasetConfig

router = APIRouter(tags=["datasets"])


@router.get("/datasets")
@router.get("/datasets/{owner}")
def datasets_list(owner: str = datasets_svc.OWNER, limit: int = 100):
    datasets = datasets_svc.get_all(owner, limit)
    return datasets


@router.get("/datasets/{owner}/{name}")
def datasets_get(owner: str, name: str):
    dataset = datasets_svc.get(owner, name)
    return dataset


# TODO: rename configs routes; not really explicit
@router.get("/configs")
def datasets_configs_list(dataset_name: str = None):
    configs = datasets_svc.list_configs(dataset_name)
    return configs


@router.post("/configs")
def datasets_configs_add(config: DatasetConfig):
    datasets_svc.add_config(config)
    return {f"{config.name}": "config uploaded"}


@router.get("/configs/{name}")
def datasets_configs_get(name: str, dataset_name: str = None):
    config = datasets_svc.get_config(name, dataset_name)
    return config

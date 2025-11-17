from fastapi import APIRouter, HTTPException
from app.evaluate.schemas import EVALUATE_INPUTS
from app.evaluate.service import tasks as evaluate_tasks
from app.evaluate import service as evaluate_svc

router = APIRouter()


@router.on_event("startup")
async def evaluate_startup():
    await evaluate_svc.start_worker()


@router.post("/evaluate")
async def start_test(inputs: EVALUATE_INPUTS):
    try:
        task_data = await evaluate_svc.add_task(inputs)
        return task_data.model_dump()
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/evaluate")
async def evaluate_list():
    try:
        tasks = await evaluate_tasks.dict()
        return tasks
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/evaluate/{task_id}")
async def evaluate_get(task_id: str):
    try:
        task = await evaluate_tasks.get(task_id)
        return task.model_dump()
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))

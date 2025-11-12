from fastapi import APIRouter, HTTPException
from app.inference.schemas import APP_STATE, COMPLETIONS_INPUTS
import app.inference.service as inferences_svc

router = APIRouter()


@router.get("/inference")
def apps_list(state: APP_STATE = None):
    try:
        apps = inferences_svc.get_all(state)
        return apps
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/inference/{id}")
def apps_get(id: str):
    try:
        app = inferences_svc.get(id)
        return app
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/inference/{id}/start")
def apps_start(id: str, model_name: str = None):
    try:
        if model_name:
            inferences_svc.update_env(id, env_name="MODEL_NAME", env_value=model_name)
        inferences_svc.start(id)
        return {f"{id}": "started"}
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/inference/{id}/stop")
def apps_stop(id: str):
    try:
        inferences_svc.stop(id)
        return {f"{id}": "stopped"}
    except Exception as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/inference/{id}/tasks")
def apps_list_tasks(id: str):
    try:
        tasks = inferences_svc.completions_get_all(id)
        return tasks
    except Exception as error:
        return HTTPException(status_code=400, detail=str(error))


@router.post("/inference/{id}/tasks")
def apps_create_task(id: str, completions_inputs: COMPLETIONS_INPUTS):
    try:
        task_id = inferences_svc.completions_submit(
            id=id,
            prompts=completions_inputs.texts,
            prompts_params=completions_inputs.prompts_params,
            sampling_params=completions_inputs.sampling_params,
        )
        return {"task_id": task_id}
    except Exception as error:
        return HTTPException(status_code=404, detail=str(error))


@router.get("/inference/{id}/tasks/{task_id}")
def apps_get_task(id: str, task_id: str):
    try:
        task_data = inferences_svc.completions_get(id=id, task_id=task_id)
        return task_data
    except Exception as error:
        HTTPException(status_code=404, details=str(error))


@router.post("/inference/{id}/generate")
def apps_generate_completions(id: str, completions_inputs: COMPLETIONS_INPUTS):
    try:
        completions, task_data = inferences_svc.completions_pipeline(
            id=id,
            url=completions_inputs.inference_url,
            texts=completions_inputs.texts,
            prompts_params=completions_inputs.prompts_params,
            sampling_params=completions_inputs.sampling_params,
        )
        return {"completions": completions, "task_data": task_data}
    except Exception as error:
        return HTTPException(status_code=404, detail=str(error))


# @router.post("/completions")
# def url_create_task(completions_inputs: COMPLETIONS_INPUTS):
#     try:
#         task_id = inferences_svc.completions_submit(
#             inference_url=completions_inputs.inference_url,
#             prompts=completions_inputs.texts,
#             prompts_params=completions_inputs.prompts_params,
#             sampling_params=completions_inputs.sampling_params,
#         )
#         return {"task_id": task_id}
#     except Exception as error:
#         return HTTPException(status_code=400, detail=str(error))


# @router.post("/completions/generate")
# def url_completions(completions_inputs: COMPLETIONS_INPUTS):
#     try:
#         completions, task_data = inferences_svc.completions_pipeline(
#             url=completions_inputs.inference_url,
#             texts=completions_inputs.texts,
#             prompts_params=completions_inputs.prompts_params,
#             sampling_params=completions_inputs.sampling_params,
#         )
#         return {"completions": completions, "duration": task_data.get("done_at") - task_data.get("running_at")}
#     except Exception as error:
#         return HTTPException(status_code=404, detail=str(error))

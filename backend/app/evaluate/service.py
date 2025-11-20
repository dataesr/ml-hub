import asyncio
import pandas as pd
from typing import Literal
from app.logger import get_logger
from app.evaluate.schemas import EVALUATE_INPUTS, EVALUATE_TASK, EVALUATE_TASKS_STORE
from app.datasets import service as datasets_svc
from app.inference import service as inference_svc
from app.utils import json_write


logger = get_logger(__name__)

tasks = EVALUATE_TASKS_STORE()
tasks_queue = asyncio.Queue()


# TODO
def get_all():
    return


def get():
    return


# def compute_score(dataset: pd.DataFrame, formatter: Literal["json", "tsv"] = "json"):
#     dataset
#     return dataset


# TODO: allow only 100 entries
def pipeline(inference_id: str, task_id: str, inputs: EVALUATE_INPUTS) -> tuple:
    logger.info(f"▶️ Start eval of model {inputs.model_name} ({task_id})")

    # Get input texts
    dataset = datasets_svc.load(inputs.dataset_name, split=inputs.dataset_split, as_pandas=True)

    # Get prompts params
    prompts_params = {}
    if inputs.dataset_config:
        try:
            prompts_params = datasets_svc.get_config(inputs.dataset_config, inputs.dataset_name).model_dump()
        except Exception as error:
            logger.error(f"Couldnt load dataset config: {error}")
    if inputs.prompts_params:
        prompts_params.update(inputs.prompts_params)

    # Run completions pipeline
    output, task_data = inference_svc.completions_pipeline(
        inference_id,
        inputs.model_name,
        inputs=dataset,
        sampling_params=inputs.sampling_params,
        prompts_params=prompts_params,
        return_only_completions=False,
        write_results=True,
    )

    # TODO:
    # results = evaluate_completions(output)

    logger.info(f"✅ Eval {task_id} completed")


async def worker():
    while True:
        task_id, inputs = await tasks_queue.get()
        try:
            await tasks.set_running(task_id)
            result = await asyncio.to_thread(pipeline, task_id, inputs)
            await tasks.set_done(task_id=task_id, result=result)
            logger.info(f"✅ Evaluate task {task_id} done")
        except Exception as error:
            await tasks.set_error(task_id, error=str(error))
            logger.error(f"❌ Evaluate task {task_id} failed: {error}")
        finally:
            tasks_queue.task_done()


async def start_worker():
    asyncio.create_task(worker())


async def add_task(task_id: str, inputs: EVALUATE_INPUTS):
    task_id = await tasks.create()
    await tasks_queue.put((task_id, inputs))
    task_data = await tasks.get(task_id)
    return task_data

import asyncio
import time
import os
import pandas as pd
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


def pipeline(inference_id: str, task_id: str, inputs: EVALUATE_INPUTS) -> tuple:
    logger.info(f"▶️ Start evaluation of model {inputs.model_name}")

    # Get input texts
    dataset = datasets_svc.load(inputs.dataset_name, split=inputs.dataset_split, as_pandas=True)
    texts = dataset["input"].to_list()

    # Run completions pipeline
    completions, task_data = inference_svc.completions_pipeline(
        inference_id,
        inputs.model_name,
        texts,
        sampling_params=inputs.sampling_params,
    )

    # Check completions
    assert isinstance(completions, list)
    if len(completions) != len(texts):
        logger.error(f"Generated {len(completions)} completions from {len(texts)} texts")
        res = pd.DataFrame({"completions": completions})
        dataset = pd.concat([dataset, res])
    else:
        logger.info(f"✅ Generated {len(completions)}")
        dataset["completions"] = pd.Series(completions)

    # Stop inference app
    inference_svc.stop(inference_id)

    # Write results
    res_path = os.path.join(inputs.model_name, time.strftime("%Y%m%d_%H%M"))
    inference_svc.completions_write(data=dataset.to_json(orient="records"))

    logger.info(f"✅ Evaluation completed and saved on {res_path}")


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

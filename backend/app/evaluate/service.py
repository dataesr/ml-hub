import asyncio
import threading
import time
from app.logger import get_logger
from app.evaluate.schemas import EVALUATE_INPUTS, EVALUATE_TASK, EVALUATE_TASKS_STORE

logger = get_logger(__name__)

tasks = EVALUATE_TASKS_STORE()
tasks_queue = asyncio.Queue()


# TODO
def get_all():
    return


def get():
    return


def pipeline(task_id: str, inputs: EVALUATE_INPUTS):
    # fake function
    for i in range(10):
        logger.debug(f"{task_id} running...")
        time.sleep(5)

    return None


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


# async def run_test(task_id: str, inputs: EVALUATE_INPUTS):
#     async def run_test_task(task_id: str):
#         try:
#             with lock:
#                 await tasks.set_running(task_id)
#                 await asyncio.to_thread(fake_function, task_id)
#             await tasks.set_done(task_id=task_id, result="this is a result")
#             logger.info(f"✅ Evaluate task {task_id} done")
#         except Exception as error:
#             await tasks.set_error(task_id, error=str(error))
#             logger.error(f"❌ Evaluate task {task_id} failed: {error}")

#     asyncio.create_task(run_test_task(task_id))
#     task_data = await tasks.get(task_id=task_id)
#     return task_data

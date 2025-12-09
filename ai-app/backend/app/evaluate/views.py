from fastapi import APIRouter
from app.evaluate import service as evaluate_svc
from app.evaluate.schemas import EVALUATE_INPUTS

router = APIRouter(tags=["evaluate"])


@router.get("/evaluate")
def evaluate_list():
    evals = evaluate_svc.get_all()
    return evals


@router.post("/evaluate")
def evaluate_run(eval_inputs: EVALUATE_INPUTS):
    evaluate_svc.evaluate(eval_inputs)
    return {eval_inputs.dataset_name: "evaluated"}

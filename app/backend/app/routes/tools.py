import os
from fastapi import APIRouter
from core.tools.flair import flair_predict_tags

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/flair")
def flair_predict(text: str):
    tags = flair_predict_tags(text)
    return tags

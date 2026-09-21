import os
from fastapi import APIRouter
from core.tools.flair import flair_predict_tags
from core.tools.cross_encoder import cross_encoder_predict

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/flair")
def flair_predict(text: str):
    tags = flair_predict_tags(text)
    return tags


@router.post("/cross-encoder")
def encoder_predict(data: dict):
    pairs = data["pairs"]
    scores = cross_encoder_predict(pairs)
    return scores

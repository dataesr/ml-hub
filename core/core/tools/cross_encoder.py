from core.utils.logger import get_logger

logger = get_logger(__name__)

models = {}


def _load_model(model_name: str, **kwargs):
    global models
    try:
        from sentence_transformers import CrossEncoder
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "sentence-transformers is required for cross_encoder_predict. "
            "Install it with 'pip install sentence-transformers' or 'pip install ai-core[tools]'."
        ) from error

    if not model_name in models:
        models[model_name] = CrossEncoder(model_name, **kwargs)
        logger.info(f"Successfully loaded CrossEncoder model {model_name}")
    return models[model_name]


def cross_encoder_predict(pairs: list[list[str]]) -> list:
    if not pairs:
        logger.debug(f"Input pairs is empty.")
        return []

    model = _load_model("cross-encoder/ms-marco-TinyBERT-L2-v2", max_length=512)

    similarity_scores = model.predict(pairs)

    return similarity_scores.tolist()

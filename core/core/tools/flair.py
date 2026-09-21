from flair.data import Sentence
from flair.models import SequenceTagger
from core.utils.logger import get_logger

logger = get_logger(__name__)

models = {}


def _load_model(model_name: str):
    global models
    if not model_name in models:
        models[model_name] = SequenceTagger.load(model_name)
        logger.info(f"Successfully loaded SequenceTagger model {model_name}")
    return models[model_name]


def flair_predict_tags(text: str) -> list[dict]:
    model = _load_model("kalawinka/flair-ner-acknowledgments")

    sentence = Sentence(text)
    model.predict(sentence)

    entities = sentence.get_spans("ner")
    if not entities or not len(entities):
        return []

    return [entity.to_dict() for entity in entities]

from flair.data import Sentence
from flair.models import SequenceTagger

models = {}


def load_ner_model(model_name: str = "kalawinka/flair-ner-acknowledgments"):
    global models
    if not model_name in models:
        models[model_name] = SequenceTagger.load(model_name)
    return models[model_name]


def flair_predict_tags(text: str) -> list[dict]:
    model = load_ner_model()

    sentence = Sentence(text)
    model.predict(sentence)

    entities = sentence.get_spans("ner")
    if not entities or not len(entities):
        return []

    return [entity.to_dict() for entity in entities]

from mlflow.genai import Scorer
from core.scorers.common import COMMON_SCORERS
from core.scorers.acknowledgement import ACKNOWLEDGEMENT_SCORERS

SCORERS_MAPPING: dict[str, list[Scorer]] = COMMON_SCORERS
SCORERS_MAPPING["acknowledgement"] = ACKNOWLEDGEMENT_SCORERS

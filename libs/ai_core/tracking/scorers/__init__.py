from mlflow.genai import Scorer
from ai_core.tracking.scorers.common import COMMON_SCORERS
from ai_core.tracking.scorers.acknowledgement import ACKNOWLEDGEMENT_SCORERS

SCORERS_MAPPING: dict[str, list[Scorer]] = COMMON_SCORERS
SCORERS_MAPPING["acknowledgement"] = ACKNOWLEDGEMENT_SCORERS
